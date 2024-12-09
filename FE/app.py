import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import random
from lat_lon_data import get_lat_lon
from weather_data import get_weather_data
from datetime import datetime
import requests
import draw_charts as draw_charts
from astral import LocationInfo
from astral.sun import sun
from datetime import timedelta
import pytz
from database import TrafficIncidentCreate, TrafficIncident
import get_wind_direction

# page settings
st.set_page_config(
    page_title = 'Real-Time USA Accidents Dashboard',
    page_icon = '🚨',
    layout = 'wide',
)

# dashboard title
st.title("Real-Time USA Accidents Dashboard")


# # Function to connect to MongoDB
# @st.cache_resource
# def get_mongo_client_and_collection():
#     db_uri = "mongodb+srv://vinhdaovinh1006:VinhDao1006@cluster1.0fg9v.mongodb.net/test"
#     client = MongoClient(db_uri, tls=True, tlsAllowInvalidCertificates=True)
#     db = client['accident_db']
#     collection = db['accidents']
#     return client, collection

# # Initialize MongoDB client and collection
# try:
#     client, reports_collection = get_mongo_client_and_collection()
#     st.success("Connected to MongoDB successfully!")
# except Exception as e:
#     st.error(f"Error connecting to MongoDB: {e}")

# # Function to fetch data from MongoDB
# @st.cache_data
# def fetch_accident_data():
#     try:
#         data = list(reports_collection.find({}, {"_id": 0}))
#         return pd.DataFrame(data)
#     except Exception as e:
#         st.error(f"Error fetching accident data: {e}")
#         return pd.DataFrame()  # Return an empty DataFrame on error


# global df_accidents
# # Establish connection and fetch data
# try:
#     df_accidents = fetch_accident_data()
#     st.success("Connected to MongoDB and data fetched successfully!")
# except Exception as e:
#     st.error(f"Error connecting to MongoDB: {e}")

# Refresh data
# def refresh_data():
#     fetch_accident_data.clear()  # Clear the cached data
#     global df_accidents
#     df_accidents = fetch_accident_data()
#     st.success("Data refreshed!")
#     return df_accidents

df_cities = pd.read_csv("uscities.csv")

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
            states = df_cities["state_id"].unique()
            selected_state = st.selectbox("Choose a State:", states)

        if granularity == "City":
            cities = df_cities[df_cities["state_id"] == selected_state]["city"].unique()
            selected_city = st.selectbox("Choose a City:", cities)

    for seconds in range(10): # for testing 300*10 = 3000s
    #while True: # for real use
        # prepare data, dataframe and variables for all visualization

        kp1_value, kp1_delta, kp2_value, kp2_delta, kp3_value, kp3_delta = draw_charts.col3(current_time)
        with placeholder.container():
            #visualize
            # Display metrics
            kp1, kp2, kp3 = st.columns(3)
            
            kp1.metric(label="Total Accidents Today", value=kp1_value, delta=kp1_delta)
            kp2.metric(label="Most Accidents City This Month", value=kp2_value, delta=kp2_delta)
            kp3.metric(label="Highest Severity Today", value=kp3_value)
            

            ### row 1 2 columns
            fig1_col1, fig2_col2 = st.columns(2)
            with fig1_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig = draw_charts.chart3(granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
            with fig2_col2:
                fig2 = draw_charts.chart4(granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig2, use_container_width=True)

            ### row 2 2 columns
            fig3_col1, fig4_col2 = st.columns(2)
            with fig3_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig3 = draw_charts.chart1(granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig3, use_container_width=True)
            with fig4_col2:
                fig4 = draw_charts.chart2(granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig4, use_container_width=True)
            
            ### row 3 2 columns
            fig5_col1, fig6_col2 = st.columns(2)
            with fig5_col1:
                #st.markdown("### First Chart")

                # Generate the chart
                fig5 = draw_charts.chart5(granularity, state=selected_state, city=selected_city)

                # Display the chart
                st.plotly_chart(fig5, use_container_width=True)
            with fig6_col2:
                fig6 = draw_charts.chart6(granularity, state=selected_state, city=selected_city)
                # Display the chart
                st.plotly_chart(fig6, use_container_width=True)

            time.sleep(1200)

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

    # Checkboxes for road features
    amenity = st.checkbox("Amenity")
    bump = st.checkbox("Bump")
    crossing = st.checkbox("Crossing")
    give_way = st.checkbox("Give Way")
    junction = st.checkbox("Junction")
    no_exit = st.checkbox("No Exit")
    railway = st.checkbox("Railway")
    roundabout = st.checkbox("Roundabout")
    station = st.checkbox("Station")
    stop = st.checkbox("Stop")
    traffic_calming = st.checkbox("Traffic Calming")
    traffic_signal = st.checkbox("Traffic Signal")
    turning_loop = st.checkbox("Turning Loop")

    description = st.text_area("Description of the Accident")
    severity = st.selectbox("Severity", ["1", "2", "3", "4"])

    # Duration input: how long did the accident last? (in minutes)
    duration_minutes = st.number_input("How long did the accident last? (in minutes)", min_value=1, value=30)

    # Button to submit a report
    # Centered, compact submit button
    col1, col2, col3 = st.columns([3,1,3])
    with col2:
        submitted = st.button("Submit", type="primary")
        predicted_severity = st.button("Predict Severity")
        

    if submitted:
        # Save to MongoDB
        
        # get lat, lon
        address = street + " " + city + " " + county + " " + state
        lat_lon = get_lat_lon(address)

        if lat_lon is None:
            st.error("Address not found! Please check the details and try again.")
        else:
            lat, lon = lat_lon
            # get weather data
            weather_data = get_weather_data(lat, lon)
            print(address)
            print(weather_data)
            
            ## highest_id = 0
            
            ## last_record = reports_collection.find_one({}, sort=[("_id", pymongo.DESCENDING)])

            ## if last_record:
            ##     highest_id = int(last_record["ID"].split("-")[1])

            # If collection is empty, start ID from 1
            ## new_id = f"A-{highest_id + 1 if highest_id > 0 else 1}"
            # for report in reports_collection.find().sort([("ID", pymongo.DESCENDING)]).limit(1):
            #     highest_id = int(report["ID"].split("-")[1])

            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            round_time = start_time

            weather_main = weather_data.get("main", {})
            weather_wind = weather_data.get("wind", {})
            weather_conditions = weather_data.get("weather", [{}])[0]
            
            weather_report = {
                "weather_timestamp": round_time,
                "temperature_f": round((weather_main.get("temp", 0) - 273.15) * 9/5 + 32, 2),
                "wind_chill_f": "",
                "humidity_percent": weather_main.get("humidity", ""),
                "pressure_in": round(weather_main.get("pressure", 0) * 0.02953, 2),
                "visibility_mi": round(weather_data.get("visibility", 0) / 1609.34, 2),
                "wind_direction": weather_wind.get("deg", 0),
                "wind_speed_mph": round(weather_wind.get("speed", 0) * 2.23694, 2),
                "precipitation_in": weather_data.get("rain", {}).get("1h", 0),
                "weather_condition": weather_conditions.get("main", "Clear")
            }

            if weather_report["weather_condition"] == "Clouds":
                weather_report["weather_condition"] = "Cloudy"

            wind_direction_map = {
                0: 'Calm',  # Calm winds
                1: 'N',     # North
                2: 'NE',    # North-East
                3: 'E',     # East
                4: 'SE',    # South-East
                5: 'S',     # South
                6: 'SW',    # South-West
                7: 'W',     # West
                8: 'NW',    # North-West
                360: 'Calm',  # Calm (for 360 degrees)
            }

            final_wind_direction =  get_wind_direction.get_wind_direction(weather_report.get("wind_direction"), weather_report.get("wind_speed_mph"))

            # Example location for now (modify as needed based on state/city input)
            location = LocationInfo(city, "US", "UTC", lat, lon)

            # Get current sun times for the location
            s = sun(location.observer, date=datetime.now().date())

            # Assume s['sunrise'] and s['sunset'] have a timezone (e.g., UTC or any other)
            timezone = s['sunrise'].tzinfo  # Extract timezone from the datetime
            current_time = datetime.now(pytz.utc).astimezone(timezone)  # Localize to match sunrise/sunset


            # st.write(s.keys())
            # Determine day or night
            sunrise_sunset = "Day" if s['sunrise'] <= current_time <= s['sunset'] else "Night"
            civil_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"
            nautical_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"
            astronomical_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"

            # report = {
            #     "ID": new_id,
            #     "Source": "Source2",
            #     "Severity": severity,
            #     "Start_Time": start_time,
            #     "End_Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            #     "Start_Lat": lat,
            #     "Start_Lng": lon,
            #     "End_Lat": "",
            #     "End_Lng": "",
            #     "Distance(mi)": 0,
            #     "Description": description,
            #     "Street": street,
            #     "City": city,
            #     "County": county,
            #     "State": state,
            #     "Zipcode": 0,
            #     "Country": "US",
            #     "Timezone": "US/Pacific",
            #     "Airport_Code": "",
            #     **weather_report,
            #     "Amenity": amenity,
            #     "Bump": bump,
            #     "Crossing": crossing,
            #     "Give_Way": give_way,
            #     "Junction": junction,
            #     "No_Exit": no_exit,
            #     "Railway": railway,
            #     "Roundabout": roundabout,
            #     "Station": station,
            #     "Stop": stop,
            #     "Traffic_Calming": traffic_calming,
            #     "Traffic_Signal": traffic_signal,
            #     "Turning_Loop": turning_loop,
            #     "Sunrise_Sunset": sunrise_sunset,
            #     "Civil_Twilight": civil_twilight,
            #     "Nautical_Twilight": nautical_twilight,
            #     "Astronomical_Twilight": astronomical_twilight
            # }


            # report = TrafficIncidentCreate(
            #     severity=severity,
            #     start_time=start_time,
            #     end_time=end_time,
            #     start_lat=lat,
            #     start_lng=lon,
            #     description=description,
            #     street=street,
            #     city=city,
            #     county=county,
            #     state=state,
            #     weather_timestamp=round_time,
            #     temperature_f=weather_report.get("temperature_f"),
            #     humidity_percent=weather_report.get("humidity_percent"),
            #     pressure_in=weather_report.get("pressure_in"),
            #     visibility_mi=weather_report.get("visibility_mi"),
            #     wind_direction=final_wind_direction,
            #     wind_speed_mph=weather_report.get("wind_speed_mph"),
            #     precipitation_in=weather_report.get("precipitation_in"),
            #     weather_condition=weather_report.get("weather_condition"),
            #     amenity=amenity,
            #     bump=bump,
            #     crossing=crossing,
            #     give_way=give_way,
            #     junction=junction,
            #     no_exit=no_exit,
            #     railway=railway,
            #     roundabout=roundabout,
            #     station=station,
            #     stop=stop,
            #     traffic_calming=traffic_calming,
            #     traffic_signal=traffic_signal,
            #     turning_loop=turning_loop,
            #     sunrise_sunset=sunrise_sunset,
            #     civil_twilight=civil_twilight,
            #     nautical_twilight=nautical_twilight,
            #     astronomical_twilight=astronomical_twilight
            # )

            report = {
                "severity": severity,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "start_lat": lat,
                "start_lng":  lon,
                "description":  description,
                "street":  street,
                "city":  city,
                "county":  county,
                "state":  state,
                "weather_timestamp":  round_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_f":  weather_report.get("temperature_f"),
                "humidity_percent":  weather_report.get("humidity_percent"),
                "pressure_in":  weather_report.get("pressure_in"),
                "visibility_mi":  weather_report.get("visibility_mi"),
                "wind_direction":  final_wind_direction,
                "wind_speed_mph":  weather_report.get("wind_speed_mph"),
                "precipitation_in":  weather_report.get("precipitation_in"),
                "weather_condition":  weather_report.get("weather_condition"),
                "amenity":  amenity,
                "bump":  bump,
                "crossing":  crossing,
                "give_way":  give_way,
                "junction":  junction,
                "no_exit":  no_exit,
                "railway":  railway,
                "roundabout":  roundabout,
                "station":  station,
                "stop":  stop,
                "traffic_calming":  traffic_calming,
                "traffic_signal":  traffic_signal,
                "turning_loop":  turning_loop,
                "sunrise_sunset":  sunrise_sunset,
                "civil_twilight":  civil_twilight,
                "nautical_twilight":  nautical_twilight,
                "astronomical_twilight":  astronomical_twilight
                }
                
            
            #  #to insert to postgresql
            # reports_collection.insert_one(report)
            
            response_data_model = requests.post(
                "http://127.0.0.1:8000/accident", 
                json=report
            )
            if response_data_model.status_code != 200:
                raise ValueError(f"API error: {response_data_model.status_code}, {response_data_model.text}")
            st.success("Report submitted successfully!")

    if predicted_severity:
        # Save to MongoDB
        
        # get lat, lon
        address = street + " " + city + " " + county + " " + state
        lat_lon = get_lat_lon(address)

        if lat_lon is None:
            st.error("Address not found! Please check the details and try again.")
        else:
            lat, lon = lat_lon
        
            # get weather data
            weather_data = get_weather_data(lat, lon)
            print(address)
            print(weather_data)
            
            ## highest_id = 0
            
            ## last_record = reports_collection.find_one({}, sort=[("_id", pymongo.DESCENDING)])

            ## if last_record:
            ##     highest_id = int(last_record["ID"].split("-")[1])

            # If collection is empty, start ID from 1
            ## new_id = f"A-{highest_id + 1 if highest_id > 0 else 1}"
            # for report in reports_collection.find().sort([("ID", pymongo.DESCENDING)]).limit(1):
            #     highest_id = int(report["ID"].split("-")[1])

            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            round_time = start_time

            weather_main = weather_data.get("main", {})
            weather_wind = weather_data.get("wind", {})
            weather_conditions = weather_data.get("weather", [{}])[0]
            
            weather_report = {
                "weather_timestamp": round_time,
                "temperature_f": round((weather_main.get("temp", 0) - 273.15) * 9/5 + 32, 2),
                "wind_chill_f": "",
                "humidity_percent": weather_main.get("humidity", ""),
                "pressure_in": round(weather_main.get("pressure", 0) * 0.02953, 2),
                "visibility_mi": round(weather_data.get("visibility", 0) / 1609.34, 2),
                "wind_direction": weather_wind.get("deg", 0),
                "wind_speed_mph": round(weather_wind.get("speed", 0) * 2.23694, 2),
                "precipitation_in": weather_data.get("rain", {}).get("1h", 0),
                "weather_condition": weather_conditions.get("main", "Clear")
            }

            if weather_report["weather_condition"] == "Clouds":
                weather_report["weather_condition"] = "Cloudy"

            wind_direction_map = {
                0: 'Calm',  # Calm winds
                1: 'N',     # North
                2: 'NE',    # North-East
                3: 'E',     # East
                4: 'SE',    # South-East
                5: 'S',     # South
                6: 'SW',    # South-West
                7: 'W',     # West
                8: 'NW',    # North-West
                360: 'Calm',  # Calm (for 360 degrees)
            }

            final_wind_direction =  get_wind_direction.get_wind_direction(weather_report.get("wind_direction"), weather_report.get("wind_speed_mph"))

            # Example location for now (modify as needed based on state/city input)
            location = LocationInfo(city, "US", "UTC", lat, lon)

            # Get current sun times for the location
            s = sun(location.observer, date=datetime.now().date())

            # Assume s['sunrise'] and s['sunset'] have a timezone (e.g., UTC or any other)
            timezone = s['sunrise'].tzinfo  # Extract timezone from the datetime
            current_time = datetime.now(pytz.utc).astimezone(timezone)  # Localize to match sunrise/sunset


            # st.write(s.keys())
            # Determine day or night
            sunrise_sunset = "Day" if s['sunrise'] <= current_time <= s['sunset'] else "Night"
            civil_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"
            nautical_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"
            astronomical_twilight = "Day" if s['dawn'] <= current_time <= s['dusk'] else "Night"

            report = {
                "severity": severity,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "start_lat": lat,
                "start_lng":  lon,
                "description":  description,
                "street":  street,
                "city":  city,
                "county":  county,
                "state":  state,
                "weather_timestamp":  round_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_f":  weather_report.get("temperature_f"),
                "humidity_percent":  weather_report.get("humidity_percent"),
                "pressure_in":  weather_report.get("pressure_in"),
                "visibility_mi":  weather_report.get("visibility_mi"),
                "wind_direction":  final_wind_direction,
                "wind_speed_mph":  weather_report.get("wind_speed_mph"),
                "precipitation_in":  weather_report.get("precipitation_in"),
                "weather_condition":  weather_report.get("weather_condition"),
                "amenity":  amenity,
                "bump":  bump,
                "crossing":  crossing,
                "give_way":  give_way,
                "junction":  junction,
                "no_exit":  no_exit,
                "railway":  railway,
                "roundabout":  roundabout,
                "station":  station,
                "stop":  stop,
                "traffic_calming":  traffic_calming,
                "traffic_signal":  traffic_signal,
                "turning_loop":  turning_loop,
                "sunrise_sunset":  sunrise_sunset,
                "civil_twilight":  civil_twilight,
                "nautical_twilight":  nautical_twilight,
                "astronomical_twilight":  astronomical_twilight
                }

            # Make an API request or call the model
            prediction_response = requests.post(
                "http://127.0.0.1:8000/predict", 
                json=report
            )

            st.success(f"The predicted severity of the accident is: {prediction_response.text}")
            # if prediction_response.status_code == 200:
            #     predicted_severity = prediction_response.json().get("predicted_severity")
            #     st.success(f"The predicted severity of the accident is: {predicted_severity}")
            # else:
            #     st.error(f"Error in severity prediction: {prediction_response.status_code}")