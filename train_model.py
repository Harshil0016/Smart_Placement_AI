import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score

BASE=Path(__file__).resolve().parent
df=pd.read_csv(BASE/"dataset.csv")
MODEL_DIR=BASE/"models"
MODEL_DIR.mkdir(exist_ok=True)

features=["gender","age","branch","college_tier","city","tenth_percentage","twelfth_percentage","cgpa",
"backlogs","attendance_percentage","internship","internship_months","projects","certifications",
"coding_skill","communication_skill","aptitude_score","technical_skill","hackathon_participation",
"extracurricular","preferred_domain"]

numeric=["age","tenth_percentage","twelfth_percentage","cgpa","backlogs","attendance_percentage",
"internship_months","projects","certifications","coding_skill","communication_skill","aptitude_score","technical_skill"]
categorical=["gender","branch","college_tier","city","internship","hackathon_participation","extracurricular","preferred_domain"]

num_pipe=Pipeline([("imputer",SimpleImputer(strategy="median"))])
cat_pipe=Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))])
prep=ColumnTransformer([("num",num_pipe,numeric),("cat",cat_pipe,categorical)])

X=df[features]; y=df["placement_status"]
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)

clf=Pipeline([("prep",prep),("model",RandomForestClassifier(n_estimators=250,max_depth=12,random_state=42,class_weight="balanced"))])
clf.fit(Xtr,ytr)
pred=clf.predict(Xte)

placed=df[df.placement_status==1]
Xs=placed[features]; ys=placed.salary_lpa
Xtr2,Xte2,ytr2,yte2=train_test_split(Xs,ys,test_size=.2,random_state=42)

prep2=ColumnTransformer([("num",num_pipe,numeric),("cat",cat_pipe,categorical)])
reg=Pipeline([("prep",prep2),("model",RandomForestRegressor(n_estimators=250,max_depth=14,random_state=42))])
reg.fit(Xtr2,ytr2)
sp=reg.predict(Xte2)

metrics={
"accuracy":float(accuracy_score(yte,pred)),
"precision":float(precision_score(yte,pred,zero_division=0)),
"recall":float(recall_score(yte,pred,zero_division=0)),
"f1":float(f1_score(yte,pred,zero_division=0)),
"mae":float(mean_absolute_error(yte2,sp)),
"rmse":float(np.sqrt(mean_squared_error(yte2,sp))),
"r2":float(r2_score(yte2,sp))
}

joblib.dump(clf,MODEL_DIR/"placement_model.pkl")
joblib.dump(reg,MODEL_DIR/"salary_model.pkl")
joblib.dump({"features":features,"metrics":metrics},MODEL_DIR/"metadata.pkl")

print("Models trained successfully")
print(metrics)
