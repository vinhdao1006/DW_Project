import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import joblib

# Load the dataset
data = pd.read_csv("US_Accidents_March23_balanced.csv")

# Features and target
features = ['Start_Lat', 'Start_Lng', 'City', 'State', 'Weather_Condition']
target = 'Severity'

# Select and preprocess relevant data
data = data[features + [target]].dropna(subset=[target])

# Handle missing values for numeric columns
numeric_columns = ['Start_Lat', 'Start_Lng']
imputer = SimpleImputer(strategy='mean')
data[numeric_columns] = imputer.fit_transform(data[numeric_columns])

# Encode categorical variables
categorical_columns = ['City', 'State', 'Weather_Condition']
label_encoders = {}
for col in categorical_columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))
    label_encoders[col] = le

# Prepare features and target
X = data[features]
y = data[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save the model and encoders
joblib.dump({'model': model, 'encoders': label_encoders}, "injury_severity_model.joblib")
print("Model saved as injury_severity_model.joblib")
