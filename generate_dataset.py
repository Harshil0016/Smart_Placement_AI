import pandas as pd
import numpy as np
import random
import math
from pathlib import Path

random.seed(42)
np.random.seed(42)

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "dataset.csv"

branches = ["Computer Engineering","Information Technology","Mechanical Engineering",
            "Civil Engineering","Electrical Engineering","Electronics Engineering"]
cities = ["Surat","Ahmedabad","Vadodara","Rajkot","Mumbai","Pune","Bangalore","Delhi","Hyderabad","Chennai"]
domains = ["Software Development","Data Science","Web Development","Testing","Cloud Computing","Networking"]

rows = []

for i in range(1, 1201):
    gender = random.choice(["Male","Female"])
    age = random.randint(20,24)
    branch = random.choice(branches)
    college_tier = random.choice(["Tier 1","Tier 2","Tier 3"])
    city = random.choice(cities)
    tenth = round(random.uniform(55,95),2)
    twelfth = round(random.uniform(55,95),2)
    cgpa = round(random.uniform(5.5,9.8),2)
    backlogs = random.choices([0,1,2,3], weights=[70,18,9,3])[0]
    attendance = round(random.uniform(60,98),2)
    internship = random.choice(["Yes","No"])
    internship_months = random.randint(0,12) if internship == "Yes" else 0
    projects = random.randint(0,5)
    certifications = random.randint(0,6)
    coding = random.randint(1,10)
    communication = random.randint(1,10)
    aptitude = random.randint(40,100)
    technical = random.randint(1,10)
    hackathon = random.choice(["Yes","No"])
    extracurricular = random.choice(["Yes","No"])
    domain = random.choice(domains)

    score = 0
    score += (cgpa-5.5)*12
    score += (tenth-55)*0.35
    score += (twelfth-55)*0.35
    score += (attendance-60)*0.25
    score += coding*2.5 + communication*1.5 + technical*2.5
    score += aptitude*0.12 + projects*4 + certifications*2 + internship_months*2
    if internship == "Yes": score += 8
    if hackathon == "Yes": score += 5
    if extracurricular == "Yes": score += 2
    if college_tier == "Tier 1": score += 8
    elif college_tier == "Tier 2": score += 4
    score -= backlogs*8

    probability = 1/(1+math.exp(-(score-85)/12))
    placement = 1 if random.random() < probability else 0

    if placement:
        salary = 2.5 + cgpa*.65 + coding*.18 + technical*.20 + projects*.35 + certifications*.12 + internship_months*.15
        if college_tier == "Tier 1": salary += 1.5
        elif college_tier == "Tier 2": salary += .7
        salary = round(max(2.5, salary + random.uniform(-.5,1.5)),2)

        if coding >= 8 and technical >= 8: role = "Software Developer"
        elif aptitude >= 80 and technical >= 7: role = "Data Analyst"
        elif domain == "Testing": role = "QA Engineer"
        elif domain == "Cloud Computing": role = "Cloud Support Engineer"
        elif domain == "Networking": role = "Network Engineer"
        else: role = "Web Developer"
    else:
        salary = 0
        role = "Not Placed"

    rows.append([f"STU{i:04d}",gender,age,branch,college_tier,city,tenth,twelfth,cgpa,backlogs,
                 attendance,internship,internship_months,projects,certifications,coding,
                 communication,aptitude,technical,hackathon,extracurricular,domain,placement,salary,role])

columns = ["student_id","gender","age","branch","college_tier","city","tenth_percentage",
"twelfth_percentage","cgpa","backlogs","attendance_percentage","internship","internship_months",
"projects","certifications","coding_skill","communication_skill","aptitude_score","technical_skill",
"hackathon_participation","extracurricular","preferred_domain","placement_status","salary_lpa","job_role"]

df = pd.DataFrame(rows, columns=columns)
df.to_csv(DATA_FILE,index=False)

print(f"Created {len(df)} records")
print("Placed:", int(df.placement_status.sum()))
print("Not Placed:", int((df.placement_status==0).sum()))
