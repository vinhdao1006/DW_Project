import streamlit as st
import pandas as pd
import plotly.express as px
import requests


def col3(df_accidents, current_time):
    #### Total accident ####
        # Filter data for the selected day
        df_accidents['Start_Time'] = pd.to_datetime(df_accidents['Start_Time'], format='%Y/%m/%d %H:%M:%S.%f')  #mixed, '%Y/%m/%d %H:%M:%S.%f'
        current_day = current_time.date()
        previous_day = (current_time - pd.Timedelta(days=1)).date()

        # Get accidents for the current day
        current_day_accidents = df_accidents[df_accidents['Start_Time'].dt.date == current_day]
        total_current_day = len(current_day_accidents)

        # Get accidents for the previous day
        previous_day_accidents = df_accidents[df_accidents['Start_Time'].dt.date == previous_day]
        total_previous_day = len(previous_day_accidents)
        
        # Calculate percentage increase
        if total_previous_day == 0:
            percent_increase = "N/A (No accidents on the previous day)"
        else:
            percent_increase = f"{((total_current_day - total_previous_day) / total_previous_day) * 100}% from yesterday"
        
        value1 = total_current_day
        delta1 = percent_increase

        #### Most accident city THIS MONTH####
        # Filter data for the current month
        current_month_start = current_time.replace(day=1)  # Start of the current month
        current_month_end = (current_month_start + pd.DateOffset(months=1)).replace(day=1) - pd.Timedelta(seconds=1)
        #print(current_time, current_month_start, current_month_end)

        # Filter accidents for the current month
        current_month_accidents = df_accidents[
            (df_accidents["Start_Time"] >= current_month_start) &
            (df_accidents["Start_Time"] <= current_month_end)
        ]

        # Group by City to calculate accident counts
        city_accident_counts_month = (
            current_month_accidents.groupby("City")
            .size()
            .reset_index(name="Accident_Count")
            .sort_values("Accident_Count", ascending=False)
        )
        if not city_accident_counts_month.empty:
            # Get city with most accidents this month
            most_accidents_city = city_accident_counts_month.iloc[0]  # First row (highest count)
            most_accidents_name = most_accidents_city["City"]
            most_accidents_total = most_accidents_city["Accident_Count"]

            # Get city with least accidents this month (excluding cities with 0)
            least_accidents_city = city_accident_counts_month.iloc[-1]  # Last row (lowest count)
            least_accidents_name = least_accidents_city["City"]
            least_accidents_total = least_accidents_city["Accident_Count"]

            # Avoid division by zero or undefined data
            if least_accidents_total == 0 or most_accidents_name == least_accidents_name:
                delta_text = "N/A (No other city to compare)"
            else:
                delta_text = f"Least Accidents City: {least_accidents_name} with {least_accidents_total} accidents"
        else:
            most_accidents_name = "No Data"
            most_accidents_total = 0
            delta_text = "N/A"

        value2 = f"{most_accidents_name} with {most_accidents_total} accidents"
        delta2 = delta_text
        #### Highest severity today ####
        # Filter accidents for today
        severity_today = (
            current_day_accidents["Severity"]
            .value_counts()
            .reset_index(name="Accident_Count")
            .rename(columns={"index": "Severity"})
            .sort_values("Accident_Count", ascending=False)
        )

        if not severity_today.empty:
            highest_severity_today = severity_today.iloc[0]  # Severity with highest accidents today
            highest_severity_today_level = highest_severity_today["Severity"]
            highest_severity_today_count = highest_severity_today["Accident_Count"]
        else:
            highest_severity_today_level = "No Data"
            highest_severity_today_count = 0

        # Filter accidents for yesterday
        severity_yesterday = (
            previous_day_accidents["Severity"]
            .value_counts()
            .reset_index(name="Accident_Count")
            .rename(columns={"index": "Severity"})
            .sort_values("Accident_Count", ascending=False)
        )

        if not severity_yesterday.empty:
            highest_severity_yesterday = severity_yesterday.iloc[0]  # Severity with highest accidents yesterday
            highest_severity_yesterday_level = highest_severity_yesterday["Severity"]
            highest_severity_yesterday_count = highest_severity_yesterday["Accident_Count"]
        else:
            highest_severity_yesterday_level = "No Data"
            highest_severity_yesterday_count = 0

        # Set delta text
        if highest_severity_today_count > 0 and highest_severity_yesterday_count > 0:
            delta_text1 = (
                f"Yesterday: Severity {highest_severity_yesterday_level} with {highest_severity_yesterday_count} accidents"
            )
        else:
            delta_text1 = "No data for yesterday"

        value3 = f"Severity {highest_severity_today_level} with {highest_severity_today_count} accidents"
        delta3 = delta_text1

        return value1, delta1, value2, delta2, value3, delta3

        

def chart1(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # filtered_df["Month"] = filtered_df["Start_Time"].dt.to_period("M")
    # severity_counts = (
    #     filtered_df.groupby(["Month", "Severity"])
    #     .size()
    #     .reset_index(name="Accident_Count")
    # )

    # trend_counts = (
    #     filtered_df.groupby("Month").size().reset_index(name="Total_Accidents")
    # )

    # combined_data = pd.merge(
    #     severity_counts, trend_counts, on="Month", how="left"
    # )

    # combined_data["Month"] = combined_data["Month"].dt.to_timestamp()

    response = requests.get(
        "http://127.0.0.1:8000/chart/1", 
        params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    combined_data = pd.DataFrame(data)

    combined_data["Month"] = pd.to_datetime(combined_data["month"], format="%Y-%m")

    new_df = combined_data.groupby("Month", as_index=False)["count"].sum()
    
    fig = px.bar(
        combined_data,
        x="Month",
        y="count",
        color="Severity",
        labels={"Accident_Count": "Number of Accidents"},
        opacity=0.7,
        title=f"Monthly Accident Trends and Severity Levels ({granularity})",
    )

    fig.add_scatter(
        x=new_df["Month"],
        y=new_df["count"],
        mode="lines+markers",
        name="Total Accidents",
        line=dict(color="black", width=2),
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Month",
        yaxis_title="Number of Accidents",
        legend_title="Legend",
        hovermode="x unified",
        height=600,
    )

    return fig

def chart2(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # filtered_df["Year_Month"] = filtered_df["Start_Time"].dt.to_period("M").astype(str)

    # weather_severity_counts = (
    #     filtered_df.groupby(["Year_Month", "Weather_Condition", "Severity"])
    #     .size()
    #     .reset_index(name="Accident_Count")
    # )

    # # Ensure all severities are included
    # all_severities = [1, 2, 3, 4, 5]
    # all_weather_conditions = filtered_df["Weather_Condition"].unique()
    # all_year_months = filtered_df["Year_Month"].unique()

    # full_grid = pd.MultiIndex.from_product(
    #     [all_year_months, all_weather_conditions, all_severities],
    #     names=["Year_Month", "Weather_Condition", "Severity"]
    # )

    # weather_severity_counts = (
    #     weather_severity_counts.set_index(["Year_Month", "Weather_Condition", "Severity"])
    #     .reindex(full_grid, fill_value=0)
    #     .reset_index()
    # )

    response = requests.get(
        "http://127.0.0.1:8000/chart/2", 
        params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    weather_severity_counts = pd.DataFrame(data)


    fig = px.bar(
        weather_severity_counts,
        x="Weather_Condition",
        y="count",
        color="Severity",
        animation_frame="month",
        labels={
            "Weather_Condition": "Weather Condition",
            "count": "Number of Accidents",
            "Severity": "Severity Level",
            "month": "Time (Year-Month)",
        },
        title=f"Monthly Accident Trends by Weather Condition and Severity ({granularity})",
        height=600,
    )
    return fig


def chart3(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # filtered_df["Year_Month"] = (
    #     filtered_df["Start_Time"].dt.to_period("M").astype(str)
    # )  # Format: "YYYY-MM"


    response = requests.get(
        "http://127.0.0.1:8000/chart/3", 
        params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    filtered_df = pd.DataFrame(data)

    fig = px.density_mapbox(
        filtered_df,
        lat="grid_lat",
        lon="grid_lng",
        z="accident_count", 
        animation_frame="month",
        radius=10,
        opacity=1,
        mapbox_style="carto-positron",
        color_continuous_scale="inferno",
        title=f"Monthly Accident Density Map ({granularity})",
        labels={"month": "Time (Year-Month)", "accident_count": "Accidents"},
        center={"lat": filtered_df["grid_lat"].mean(),
            "lon": filtered_df["grid_lng"].mean(),},
        zoom=2.95 if granularity == "USA" else 5,
    )

    fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            title="Density",
            thicknessmode="pixels",
            thickness=20,
            lenmode="fraction",
            len=0.5,
        ),
    )

    return fig


def chart4(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # severity_colors = {
    #     1: "blue",
    #     2: "green",
    #     3: "yellow",
    #     4: "orange",
    #     5: "red",
    # }
    
    # filtered_df["Year_Month"] = (
    #     filtered_df["Start_Time"].dt.to_period("M").astype(str)
    # )  # Format: "YYYY-MM"

    response = requests.get(
        "http://127.0.0.1:8000/chart/4", 
        params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    filtered_df = pd.DataFrame(data)

    severity_colors = {
        '1': "#0000FF",
        '2': "#7FFF00",
        '3': "#FF00FF",
        '4': "#FF8C00",
        '5': "#A52A2A",
    }

    fig = px.scatter_mapbox(
        filtered_df,
        lat="grid_lat",
        lon="grid_lng",
        color="Severity",
        size="accident_count",
        animation_frame="month",
        color_discrete_map=severity_colors,
        hover_data=["grid_lat", "grid_lng", "Severity", "accident_count"],
        center={"lat": 37.0902, "lon": -95.7129},
        opacity=1,
        size_max=40,
        zoom=3 if granularity == "USA" else 5,
        title="Accidents by Severity",
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={
            "lat": filtered_df["grid_lat"].mean(),
            "lon": filtered_df["grid_lng"].mean(),
        },
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
    )

    return fig


def chart5(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # road_types = [
    #     "Amenity", "Bump", "Crossing", "Give_Way", "Junction", "No_Exit", "Railway",
    #     "Roundabout", "Station", "Stop", "Traffic_Calming", "Traffic_Signal", "Turning_Loop"
    # ]

    # filtered_df["Year"] = pd.to_datetime(filtered_df["Start_Time"]).dt.year

    # severity_road_counts = (
    #     filtered_df.groupby(["Year", "Severity"])[road_types]
    #     .sum()
    #     .reset_index()
    # )

    # severity_road_counts["Severity"] = severity_road_counts["Severity"].astype(str)

    # df_heatmap = severity_road_counts.melt(
    #     id_vars=["Year", "Severity"],
    #     var_name="Road_Type",
    #     value_name="Accident_Count"
    # )

    response = requests.get(
    "http://127.0.0.1:8000/chart/5", 
    params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    df_heatmap = pd.DataFrame(data)

    df_heatmap = df_heatmap.melt(
        id_vars=["year", "Severity"],
        var_name="Road_Type",
        value_name="Accident_Count"
    )

    fig = px.density_heatmap(
        df_heatmap,
        x="Road_Type",
        y="Severity",
        z="Accident_Count",
        animation_frame="year",
        color_continuous_scale="inferno",
        title=f"Yearly Impact of Road Types by Accident Severity ({granularity})",
        labels={
            "Road_Type": "Road Type",
            "Severity": "Accident Severity",
            "Accident_Count": "Number of Accidents",
            "year": "Year"
        },
    )

    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        xaxis_title="Road Types",
        yaxis_title="Severity",
        yaxis=dict(
            categoryorder="array",
            categoryarray=["1", "2", "3", "4", "5"],
        )
    )

    return fig


def chart6(df_accidents, granularity, state=None, city=None):
    # if granularity == "USA":
    #     filtered_df = df_accidents
    # elif granularity == "State" and state:
    #     filtered_df = df_accidents[df_accidents["State"] == state]
    # elif granularity == "City" and state and city:
    #     filtered_df = df_accidents[
    #         (df_accidents["State"] == state) & (df_accidents["City"] == city)
    #     ]
    # else:
    #     raise ValueError("Invalid granularity or missing parameters for State/City.")

    # if filtered_df.empty:
    #     raise ValueError(
    #         f"No data available for the selected criteria: granularity={granularity}, state={state}, city={city}"
    #     )

    # filtered_df["Hour"] = pd.to_datetime(filtered_df["Start_Time"]).dt.hour
    # filtered_df["Year"] = pd.to_datetime(filtered_df["Start_Time"]).dt.year

    # required_columns = ["Year", "Hour", "Severity"]
    # for col in required_columns:
    #     if col not in filtered_df.columns:
    #         raise KeyError(f"Missing required column: {col}")

    # hourly_severity = (
    #     filtered_df.groupby(["Year", "Hour", "Severity"])
    #     .size()
    #     .reset_index(name="Accident_Count")
    # )

    # hourly_severity["Severity"] = hourly_severity["Severity"].astype(str)

    response = requests.get(
    "http://127.0.0.1:8000/chart/6", 
    params={"state": state, "city": city}
    )
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    df_heatmap = pd.DataFrame(data)

    fig = px.density_heatmap(
        df_heatmap,
        x="hour",
        y="Severity",
        z="count",
        animation_frame="year",
        color_continuous_scale="inferno",
        labels={
            "hour": "Hour of Day",
            "Severity": "Accident Severity",
            "Accident_Count": "Number of Accidents",
        },
        title=f"Daily Distribution of Accident Severities Each Year ({granularity})",
    )

    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        xaxis=dict(tickmode="linear", dtick=1),
    )

    return fig