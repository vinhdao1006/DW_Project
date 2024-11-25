INSERT INTO traffic_incidents (
    severity, start_time, end_time, start_lat, start_lng, end_lat, end_lng, distance_mi, description,
    street, city, county, state, weather_timestamp, temperature_f, wind_chill_f, humidity_percent,
    pressure_in, visibility_mi, wind_direction, wind_speed_mph, precipitation_in, weather_condition,
    amenity, bump, crossing, give_way, junction, no_exit, railway, roundabout, station, stop,
    traffic_calming, traffic_signal, turning_loop, sunrise_sunset, civil_twilight, nautical_twilight,
    astronomical_twilight
) VALUES
(
    '1', NOW() - INTERVAL '2 HOURS', NOW() - INTERVAL '1 HOUR', 37.774929, -122.419416, 37.774929, -122.419416, 0.7,
    'Vehicle stalled on the shoulder.', 'Market St', 'San Francisco', 'San Francisco', 'CA',
    NOW(), 58.0, 55.0, 75.0, 30.1, 8.0, 'W', 12.0, NULL, 'Cloudy',
    FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE,
    FALSE, FALSE, FALSE, 'Day', 'Day', 'Day', 'Day'
),
(
    '3', NOW() - INTERVAL '4 HOURS', NOW() - INTERVAL '3 HOURS', 39.739236, -104.990251, 39.739236, -104.990251, 1.5,
    'Icy conditions reported on overpass.', 'Colfax Ave', 'Denver', 'Denver', 'CO',
    NOW(), 32.0, 28.0, 85.0, 29.7, 2.0, 'NE', 25.0, 0.4, 'Snow',
    FALSE, TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, TRUE,
    TRUE, TRUE, FALSE, 'Night', 'Night', 'Night', 'Night'
),
(
    '2', NOW() - INTERVAL '1 DAY', NOW() - INTERVAL '23 HOURS', 25.761681, -80.191788, 25.761681, -80.191788, 1.0,
    'Flooding on local streets.', 'Biscayne Blvd', 'Miami', 'Miami-Dade', 'FL',
    NOW(), 77.0, NULL, 90.0, 29.9, 1.0, 'SE', 15.0, 1.2, 'Rain',
    TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, TRUE, TRUE,
    FALSE, FALSE, FALSE, 'Day', 'Day', 'Day', 'Day'
),
(
    '4', NOW() - INTERVAL '12 HOURS', NOW() - INTERVAL '11 HOURS', 36.162664, -86.781602, 36.162664, -86.781602, 3.5,
    'Multi-car collision on highway.', 'I-65', 'Nashville', 'Davidson', 'TN',
    NOW(), 40.0, 35.0, 80.0, 30.0, 4.5, 'N', 18.0, NULL, 'Fog',
    FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, TRUE,
    FALSE, TRUE, FALSE, 'Night', 'Night', 'Night', 'Night'
),
(
    '2', NOW() - INTERVAL '3 HOURS', NOW() - INTERVAL '2 HOURS', 44.977753, -93.265011, 44.977753, -93.265011, 2.0,
    'Traffic lights malfunction at intersection.', 'Hennepin Ave', 'Minneapolis', 'Hennepin', 'MN',
    NOW(), 22.0, 18.0, 60.0, 30.2, 6.0, 'Variable', 10.0, 0.0, 'Clear',
    FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE,
    TRUE, TRUE, FALSE, 'Day', 'Day', 'Day', 'Day'
);
