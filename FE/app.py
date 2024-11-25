import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import random
from lat_lon_data import get_lat_lon
from weather_data import get_weather_data
from datetime import datetime
import pymongo
from pymongo.mongo_client import MongoClient
import requests
import draw_charts as draw_charts




# page settings
st.set_page_config(
    page_title = 'Real-Time USA Accidents Dashboard',
    page_icon = '🚨',
    layout = 'wide',
)

# dashboard title
st.title("Real-Time USA Accidents Dashboard")


# # Function to connect to MongoDB
@st.cache_resource
def get_mongo_client_and_collection():
    db_uri = "mongodb+srv://vinhdaovinh1006:VinhDao1006@cluster1.0fg9v.mongodb.net/test"
    client = MongoClient(db_uri, tls=True, tlsAllowInvalidCertificates=True)
    db = client['accident_db']
    collection = db['accidents']
    return client, collection

# Initialize MongoDB client and collection
try:
    client, reports_collection = get_mongo_client_and_collection()
    st.success("Connected to MongoDB successfully!")
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")

# Function to fetch data from MongoDB
@st.cache_data
def fetch_accident_data():
    try:
        data = list(reports_collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching accident data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


global df_accidents
# Establish connection and fetch data
try:
    df_accidents = fetch_accident_data()
    st.success("Connected to MongoDB and data fetched successfully!")
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")

# Refresh data
def refresh_data():
    fetch_accident_data.clear()  # Clear the cached data
    global df_accidents
    df_accidents = fetch_accident_data()
    st.success("Data refreshed!")
    return df_accidents


selected_page = st.radio("Welcome!", ["Dashboard", "Report"], horizontal=True)

# # Dashboard Page
if selected_page == "Dashboard":
    ######### only refresh data when user is on dashboard
    
    st.header("Dashboard")
    
    # creating a single-element container.
    placeholder = st.empty()

    #current_time = datetime.now()

    current_time = datetime(2016, 5, 25, 0, 0, 0)
    st.write(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    ### choosing granularity for charts
    granularity = "USA"
    with st.sidebar:
        granularity = st.radio("Choose level of data granularity:", ["USA", "State", "City"], index=0)

        selected_state, selected_city = None, None
        if granularity in ["State", "City"]:
            states = df_accidents["State"].unique()
            selected_state = st.selectbox("Choose a State:", states)

        if granularity == "City":
            cities = df_accidents[df_accidents["State"] == selected_state]["City"].unique()
            selected_city = st.selectbox("Choose a City:", cities)

    for seconds in range(10): # for testing 300*10 = 3000s
    #while True: # for real use
        # prepare data, dataframe and variables for all visualization

        kp1_value, kp1_delta, kp2_value, kp2_delta, kp3_value, kp3_delta = draw_charts.col3(df_accidents, current_time)
        df_accidents['Start_Time'] = pd.to_datetime(df_accidents['Start_Time'], format='%Y/%m/%d %H:%M:%S.%f')
        with placeholder.container():
            #visualize
            # Display metrics
            kp1, kp2, kp3 = st.columns(3)
            
            kp1.metric(label="Total Accidents Today", value=kp1_value, delta=kp1_delta)
            kp2.metric(label="Most Accidents City This Month", value=kp2_value, delta=kp2_delta)
            kp3.metric(label="Highest Severity Today", value=kp3_value, delta=kp3_delta)
            

            ### row 1 2 columns
            fig1_col1, fig2_col2 = st.columns(2)
            with fig1_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig = draw_charts.chart3(df_accidents, granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
            with fig2_col2:
                fig2 = draw_charts.chart4(df_accidents, granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig2, use_container_width=True)

            ### row 2 2 columns
            fig3_col1, fig4_col2 = st.columns(2)
            with fig3_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig3 = draw_charts.chart1(df_accidents, granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig3, use_container_width=True)
            with fig4_col2:
                fig4 = draw_charts.chart2(df_accidents, granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig4, use_container_width=True)
            
            ### row 3 2 columns
            fig5_col1, fig6_col2 = st.columns(2)
            with fig5_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig5 = draw_charts.chart5(df_accidents, granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig5, use_container_width=True)
            with fig6_col2:
                fig6 = draw_charts.chart6(df_accidents, granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig6, use_container_width=True)

            time.sleep(300)

# Report Page
st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50;  /* Green background */
            color: white;  /* White text */
            width: 100%;  /* Full width of the form */
            padding: 10px;  /* Increase padding */
            border-radius: 8px;  /* Rounded corners */
            font-size: 16px;  /* Larger font */
            font-weight: bold;  /* Bold text */
            border: none;  /* Remove default border */
            transition: background-color 0.3s;  /* Smooth color transition */
        }
        .stButton>button:hover {
            background-color: #45a049;  /* Slightly darker green on hover */
        }
        .stButton>button:active {
            background-color: #3e8e41;  /* Even darker when clicked */
        }
        </style>
        """, unsafe_allow_html=True)

if selected_page == "Report":
    st.header("Accident Report Submission")
    df = pd.read_csv("uscities.csv")
    df = df.dropna(subset=['state_id', 'county_name', 'city'])

    states = df['state_name'].unique()
    state = st.selectbox('Select State', states, index=0)
    df_state = df[df['state_name'] == state]
    
    state = df_state['state_id'].iloc[0]
    
    counties = df_state['county_name'].unique()
    county = st.selectbox('Select County', counties, index=0)
    df_county = df_state[df_state['county_name'] == county]
    
    cities = df_county['city'].unique()
    city = st.selectbox('Select City', cities, index=0)

    street = st.text_input("Street")

    description = st.text_area("Description of the Accident")
    severity = st.selectbox("Severity", ["1", "2", "3", "4", "5"])

    # Button to submit a report
    # Centered, compact submit button
    col1, col2, col3 = st.columns([3,1,3])
    with col2:
        submitted = st.button("Submit", type="primary")
        

    if submitted:
        # Save to MongoDB
        
        # get lat, lon
        address = street + " " + city + " " + county + " " + state
        lat, lon = get_lat_lon(address)
        
        # get weather data
        weather_data = get_weather_data(lat, lon)
        print(address)
        print(weather_data)
        
        highest_id = 0
        
        last_record = reports_collection.find_one({}, sort=[("_id", pymongo.DESCENDING)])

        if last_record:
            highest_id = int(last_record["ID"].split("-")[1])

        # If collection is empty, start ID from 1
        new_id = f"A-{highest_id + 1 if highest_id > 0 else 1}"
        # for report in reports_collection.find().sort([("ID", pymongo.DESCENDING)]).limit(1):
        #     highest_id = int(report["ID"].split("-")[1])

        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        round_time = start_time

        weather_main = weather_data.get("main", {})
        weather_wind = weather_data.get("wind", {})
        weather_conditions = weather_data.get("weather", [{}])[0]
        
        weather_report = {
            "Weather_Timestamp": round_time,
            "Temperature(F)": round((weather_main.get("temp", 0) - 273.15) * 9/5 + 32, 2),
            "Wind_Chill(F)": "",
            "Humidity(%)": weather_main.get("humidity", ""),
            "Pressure(in)": round(weather_main.get("pressure", 0) * 0.02953, 2),
            "Visibility(mi)": round(weather_data.get("visibility", 0) / 1609.34, 2),
            "Wind_Direction": weather_wind.get("deg", ""),
            "Wind_Speed(mph)": round(weather_wind.get("speed", 0) * 2.23694, 2),
            "Precipitation(in)": weather_data.get("rain", {}).get("1h", ""),
            "Weather_Condition": weather_conditions.get("main", "Clear")
        }

        report = {
            "ID": new_id,
            "Source": "Source2",
            "Severity": severity,
            "Start_Time": start_time,
            "End_Time": "",
            "Start_Lat": lat,
            "Start_Lng": lon,
            "End_Lat": "",
            "End_Lng": "",
            "Distance(mi)": 0,
            "Description": description,
            "Street": street,
            "City": city,
            "County": county,
            "State": state,
            "Zipcode": 0,
            "Country": "US",
            "Timezone": "US/Pacific",
            "Airport_Code": "",
            **weather_report,
            "Amenity": "False",
            "Bump": "False",
            "Crossing": "False",
            "Give_Way": "False",
            "Junction": "True",
            "No_Exit": "False",
            "Railway": "False",
            "Roundabout": "False",
            "Station": "False",
            "Stop": "False",
            "Traffic_Calming": "False",
            "Traffic_Signal": "False",
            "Turning_Loop": "False",
            "Sunrise_Sunset": "Day",
            "Civil_Twilight": "Day",
            "Nautical_Twilight": "Day",
            "Astronomical_Twilight": "Day"
        }
        
         #to insert to mongodb
        reports_collection.insert_one(report)
        
        st.success("Report submitted successfully!")