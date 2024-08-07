from flask import Flask, request, send_file, render_template
import pandas as pd
from fpdf import FPDF
import random
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        # Read the excel file
        df = pd.read_excel(file)
        
        # Separate columns into individual DataFrames
        df_dev = df[['Dev']].dropna()
        df_ba = df[['BA']].dropna()
        df_da = df[['DA']].dropna()
        
        # Generate teams
        teams = generate_teams(df_dev, df_ba, df_da)
        
        # Create PDF
        pdf_path = create_pdf(teams)
        
        return send_file(pdf_path, as_attachment=True)
    
    return "File upload failed"

def generate_teams(df_dev, df_ba, df_da):
    teams = []
    min_length = min(len(df_dev)//3, len(df_ba), len(df_da))
    
    devs = df_dev.sample(frac=1).reset_index(drop=True)
    bas = df_ba.sample(frac=1).reset_index(drop=True)
    das = df_da.sample(frac=1).reset_index(drop=True)
    
    for i in range(min_length):
        team = {
            "Devs": devs.iloc[i*3:(i+1)*3]['Dev'].tolist(),
            "BA": bas.iloc[i]['BA'],
            "DA": das.iloc[i]['DA']
        }
        teams.append(team)
    
    return teams

def create_pdf(teams):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    
    for idx, team in enumerate(teams):
        pdf.cell(200, 10, txt = f"Team {idx+1}", ln = True, align = 'C')
        pdf.cell(200, 10, txt = f"Devs:", ln = True, align = 'L')
        for dev in team["Devs"]:
            pdf.cell(200, 10, txt = dev, ln = True, align = 'L')
        pdf.cell(200, 10, txt = f"BA: {team['BA']}", ln = True, align = 'L')
        pdf.cell(200, 10, txt = f"DA: {team['DA']}", ln = True, align = 'L')
        pdf.cell(200, 10, ln = True) # Add a blank line between teams
    
    pdf_path = "teams.pdf"
    pdf.output(pdf_path)
    
    return pdf_path

if __name__ == '__main__':
    app.run(debug=True)
