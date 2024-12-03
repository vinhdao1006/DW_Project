def get_wind_direction(wind_direction_degrees, wind_speed_mph):
    # Thresholds for wind speed
    calm_threshold = 1.11846815  # mph
    variable_threshold = 6.90467669  # mph
    
    # Check if the wind is calm
    if wind_speed_mph < calm_threshold:
        return "Calm"
    
    # Check if the wind is variable
    if wind_speed_mph > variable_threshold:
        return "Variable"
    
    # Determine direction based on degrees if wind speed is between calm and variable thresholds
    if 0 <= wind_direction_degrees < 22.5 or wind_direction_degrees >= 337.5:
        return "N"
    elif 22.5 <= wind_direction_degrees < 67.5:
        return "NE"
    elif 67.5 <= wind_direction_degrees < 112.5:
        return "E"
    elif 112.5 <= wind_direction_degrees < 157.5:
        return "SE"
    elif 157.5 <= wind_direction_degrees < 202.5:
        return "S"
    elif 202.5 <= wind_direction_degrees < 247.5:
        return "SW"
    elif 247.5 <= wind_direction_degrees < 292.5:
        return "W"
    elif 292.5 <= wind_direction_degrees < 337.5:
        return "NW"
    else:
        return "Variable"  # in case of any unexpected degrees