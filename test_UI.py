import streamlit as st
import joblib
import pandas as pd

# Load the trained model and encoders
saved_model = joblib.load("injury_severity_model.joblib")
model = saved_model['model']
encoders = saved_model['encoders']

# Input fields for Streamlit
st.title("Predict Injury Severity")
inputs = {}

inputs['Start_Lat'] = st.number_input("Start Latitude", value=0.0)
inputs['Start_Lng'] = st.number_input("Start Longitude", value=0.0)
inputs['City'] = st.text_input("City", value="Unknown")
inputs['State'] = st.text_input("State", value="Unknown")
inputs['Weather_Condition'] = st.text_input("Weather Condition", value="Clear")

if st.button("Predict"):
    
    # Prepare input data
    input_data = pd.DataFrame([{
        'Start_Lat': inputs['Start_Lat'],
        'Start_Lng': inputs['Start_Lng'],
        'City': inputs['City'],
        'State': inputs['State'],
        'Weather_Condition': inputs['Weather_Condition']
    }])

    # Apply encoders to categorical inputs
    for col in ['City', 'State', 'Weather_Condition']:
        le = encoders[col]
        input_data[col] = le.transform([input_data[col].iloc[0]])

    # Make prediction
    prediction = model.predict(input_data)
    st.write(f"Predicted Severity: {prediction[0]}")
