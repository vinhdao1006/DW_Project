INSERT INTO traffic_incidents (
    severity, start_time, end_time, start_lat, start_lng, end_lat, end_lng, distance_mi, description,
    street, city, county, state, weather_timestamp, temperature_f, wind_chill_f, humidity_percent,
    pressure_in, visibility_mi, wind_direction, wind_speed_mph, precipitation_in, weather_condition,
    amenity, bump, crossing, give_way, junction, no_exit, railway, roundabout, station, stop,
    traffic_calming, traffic_signal, turning_loop, sunrise_sunset, civil_twilight, nautical_twilight,
    astronomical_twilight
) VALUES
(
    '2', NOW() - INTERVAL '1 HOUR', NOW(), 40.712776, -74.005974, 40.712776, -74.005974, 0.5,
    'Accident reported near main street.', 'Main Street', 'New York', 'New York', 'NY',
    NOW(), 50.0, 45.0, 70.0, 30.2, 5.0, 'NE', 10.0, 0.1, 'Rain',
    FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE,
    FALSE, TRUE, FALSE, 'Day', 'Day', 'Day', 'Day'
),
(
    '3', NOW() - INTERVAL '3 HOURS', NOW() - INTERVAL '2 HOURS', 34.052235, -118.243683, 34.052235, -118.243683, 1.2,
    'Traffic signal malfunction causing delay.', 'Broadway', 'Los Angeles', 'Los Angeles', 'CA',
    NOW(), 65.0, 60.0, 50.0, 29.8, 10.0, 'SW', 5.0, NULL, 'Clear',
    FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE,
    TRUE, TRUE, FALSE, 'Day', 'Day', 'Day', 'Day'
),
(
    '4', NOW() - INTERVAL '5 HOURS', NOW() - INTERVAL '4 HOURS', 41.878113, -87.629799, 41.878113, -87.629799, 2.5,
    'Major accident blocking two lanes.', 'Michigan Ave', 'Chicago', 'Cook', 'IL',
    NOW(), 45.0, 40.0, 85.0, 30.1, 3.0, 'E', 15.0, 0.2, 'Fog',
    FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, TRUE,
    FALSE, TRUE, FALSE, 'Night', 'Night', 'Night', 'Night'
),
(
    '1', NOW() - INTERVAL '30 MINUTES', NOW() - INTERVAL '15 MINUTES', 29.760427, -95.369804, 29.760427, -95.369804, 0.8,
    'Minor collision with no injuries.', 'Westheimer Rd', 'Houston', 'Harris', 'TX',
    NOW(), 72.0, NULL, 60.0, 29.9, 7.0, 'Calm', 0.0, 0.0, 'Cloudy',
    TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE,
    FALSE, TRUE, FALSE, 'Day', 'Day', 'Day', 'Day'
),
(
    '2', NOW() - INTERVAL '6 HOURS', NOW() - INTERVAL '5 HOURS', 47.606209, -122.332069, 47.606209, -122.332069, 1.8,
    'Slippery roads causing multiple skids.', 'Pike St', 'Seattle', 'King', 'WA',
    NOW(), 38.0, 35.0, 90.0, 30.3, 2.5, 'NW', 20.0, 0.5, 'Snow',
    FALSE, TRUE, FALSE, FALSE, TRUE, FALSE, TRUE, TRUE, FALSE, TRUE,
    FALSE, TRUE, FALSE, 'Night', 'Night', 'Night', 'Night'
);