from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import subprocess, sys

BASE=Path(__file__).resolve().parent
DATA=BASE/"dataset.csv"
MODELS=BASE/"models"

if not DATA.exists():
    subprocess.run([sys.executable,"generate_dataset.py"],check=True)
if not (MODELS/"placement_model.pkl").exists():
    subprocess.run([sys.executable,"train_model.py"],check=True)

df=pd.read_csv(DATA)
clf=joblib.load(MODELS/"placement_model.pkl")
reg=joblib.load(MODELS/"salary_model.pkl")
metadata=joblib.load(MODELS/"metadata.pkl")

app=Flask(__name__)

def make_row(data):
    return pd.DataFrame([{
        "gender":data["gender"],"age":int(data["age"]),"branch":data["branch"],
        "college_tier":data["college_tier"],"city":data["city"],
        "tenth_percentage":float(data["tenth_percentage"]),
        "twelfth_percentage":float(data["twelfth_percentage"]),
        "cgpa":float(data["cgpa"]),"backlogs":int(data["backlogs"]),
        "attendance_percentage":float(data["attendance_percentage"]),
        "internship":data["internship"],"internship_months":int(data["internship_months"]),
        "projects":int(data["projects"]),"certifications":int(data["certifications"]),
        "coding_skill":int(data["coding_skill"]),
        "communication_skill":int(data["communication_skill"]),
        "aptitude_score":int(data["aptitude_score"]),
        "technical_skill":int(data["technical_skill"]),
        "hackathon_participation":data["hackathon_participation"],
        "extracurricular":data["extracurricular"],
        "preferred_domain":data["preferred_domain"]
    }])

@app.route("/")
def home():
    placed=int(df.placement_status.sum())
    return render_template("index.html",
        total=len(df),placed=placed,
        rate=round(placed/len(df)*100,1),
        avg_salary=round(df[df.placement_status==1].salary_lpa.mean(),2),
        highest=round(df.salary_lpa.max(),2))

@app.route("/predict",methods=["GET","POST"])
def predict():
    if request.method=="GET":
        return render_template("predict.html")
    data=request.form.to_dict()
    row=make_row(data)
    prob=float(clf.predict_proba(row)[0][1])*100
    placed=prob>=50
    salary=float(reg.predict(row)[0]) if placed else 0
    coding=int(data["coding_skill"]); technical=int(data["technical_skill"])
    aptitude=int(data["aptitude_score"]); domain=data["preferred_domain"]
    if coding>=8 and technical>=8: role="Software Developer"
    elif aptitude>=80 and technical>=7: role="Data Analyst"
    elif domain=="Testing": role="QA Engineer"
    elif domain=="Cloud Computing": role="Cloud Support Engineer"
    elif domain=="Networking": role="Network Engineer"
    else: role="Web Developer"
    risk="LOW" if prob>=75 else "MEDIUM" if prob>=50 else "HIGH"
    tips=[]
    if coding<7: tips.append("Improve coding practice")
    if technical<7: tips.append("Strengthen technical subjects")
    if int(data["projects"])<2: tips.append("Build more practical projects")
    if int(data["internship_months"])<3: tips.append("Try to gain internship experience")
    if aptitude<70: tips.append("Practice aptitude regularly")
    if int(data["communication_skill"])<7: tips.append("Improve communication skills")
    if not tips: tips.append("Keep building projects and preparing for interviews")
    return render_template("result.html",prob=round(prob,1),salary=round(salary,2),role=role,risk=risk,tips=tips,name=data.get("student_name","Student"))

@app.route("/analytics")
def analytics():
    branch=df.groupby("branch").agg(
        students=("student_id","count"),
        placement_rate=("placement_status","mean"),
        avg_salary=("salary_lpa",lambda x: x[x>0].mean() if (x>0).any() else 0)
    ).reset_index()
    branch["placement_rate"]=(branch["placement_rate"]*100).round(1)
    return render_template("analytics.html",branch=branch.to_dict("records"),metrics=metadata["metrics"])

@app.route("/students")
def students():
    rows=df.head(300).to_dict("records")
    return render_template("students.html",students=rows)

if __name__=="__main__":
    app.run(debug=True,host="127.0.0.1",port=5000)
