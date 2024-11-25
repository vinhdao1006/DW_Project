CREATE TYPE severity AS ENUM ('1', '2', '3', '4');
CREATE TYPE day_night AS ENUM ('Day', 'Night');
CREATE TYPE weather_condition AS ENUM ('Clear', 'Cloudy', 'Fog', 'Hail', 'Rain', 'Sand', 'Smoke', 'Snow', 'Thunderstorm', 'Tornado', 'Windy');
CREATE TYPE wind_direction AS ENUM('Calm', 'W', 'E', 'S', 'N', 'NE', 'SW', 'SE', 'NW', 'Variable');
CREATE TYPE us_state_enum AS ENUM (
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
);

CREATE TABLE traffic_incidents (
    id SERIAL PRIMARY KEY,
    severity severity,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    start_lat DOUBLE PRECISION,
    start_lng DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lng DOUBLE PRECISION,
    distance_mi DOUBLE PRECISION,
    description TEXT,
    street TEXT,
    city TEXT,
    county TEXT,
    state us_state_enum,
    weather_timestamp TIMESTAMP,
    temperature_f DOUBLE PRECISION,
    wind_chill_f DOUBLE PRECISION,
    humidity_percent DOUBLE PRECISION,
    pressure_in DOUBLE PRECISION,
    visibility_mi DOUBLE PRECISION,
    wind_direction wind_direction,
    wind_speed_mph DOUBLE PRECISION,
    precipitation_in DOUBLE PRECISION,
    weather_condition weather_condition,
    amenity BOOLEAN,
    bump BOOLEAN,
    crossing BOOLEAN,
    give_way BOOLEAN,
    junction BOOLEAN,
    no_exit BOOLEAN,
    railway BOOLEAN,
    roundabout BOOLEAN,
    station BOOLEAN,
    stop BOOLEAN,
    traffic_calming BOOLEAN,
    traffic_signal BOOLEAN,
    turning_loop BOOLEAN,
    sunrise_sunset day_night,
    civil_twilight day_night,
    nautical_twilight day_night,
    astronomical_twilight day_night,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON traffic_incidents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_end_time ON traffic_incidents(end_time);