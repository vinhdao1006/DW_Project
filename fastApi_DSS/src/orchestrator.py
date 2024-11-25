import duckdb


class DuckDBPostgresETL:
    def __init__(self, duckdb_path, postgres_config, logger):
        """
        Initialize ETL process
        duckdb_path: Path to DuckDB file
        postgres_config: Dict with host, port, database, user, password
        """
        self.duckdb_path = duckdb_path
        self.postgres_config = postgres_config
        self.conn = None
        self.logger = logger

    def setup_connection(self):
        """Setup DuckDB connection and load PostgreSQL extension"""
        try:
            self.conn = duckdb.connect(self.duckdb_path)
            self.logger.info("Successfully connected to DuckDB")

            self.conn.install_extension("postgres")
            self.conn.load_extension("postgres")

            # Attach PostgreSQL database
            self.conn.execute(f"""
                ATTACH 'dbname={self.postgres_config["database"]} user={self.postgres_config["user"]} host=127.0.0.1 password={self.postgres_config["password"]}' 
                AS postgres_db (TYPE POSTGRES, SCHEMA 'public');
            """)
            self.logger.info("Successfully connected to PostgreSQL")
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            raise

    def close(self):
        """Close DuckDB connection"""
        if self.conn:
            self.conn.close()

    def run_daily_etl(self, table_configs):
        """
        Run ETL process for configured tables
        table_configs: List of dicts with source_table and target_table
        """
        try:
            self.setup_connection()

            self.logger.info("Starting ETL")#

            # noinspection SqlNoDataSourceInspection
            # noinspection SqlDialectInspection
            # Insert new data
            self.conn.execute(f"""
            BEGIN TRANSACTION;
            
            -- First create UNIQUE constraints/indexes for the tables
            CREATE UNIQUE INDEX IF NOT EXISTS idx_environment_unique ON environment (
                amenity, bump, crossing, give_way, junction, no_exit, railway, roundabout,
                station, stop, traffic_calming, traffic_signal, turning_loop
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_twilight_unique ON twilight (
                sunrise_sunset, civil_twilight, nautical_twilight, astronomical_twilight
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_weather_unique ON weather (weather_condition);
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_wind_unique ON wind (wind_direction);
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_location_unique ON location (street, city, county, state);
            

            -- Insert into environment
            INSERT INTO environment (
                Environment_ID, Amenity, Bump, Crossing, Give_Way, Junction, No_Exit, Railway, Roundabout,
                Station, Stop, Traffic_Calming, Traffic_Signal, Turning_Loop
            )
            SELECT DISTINCT
                nextval('seq_environment_id'),
                amenity, bump, crossing, give_way, junction, no_exit, railway, roundabout,
                station, stop, traffic_calming, traffic_signal, turning_loop
            FROM postgres_db.public.traffic_incidents
            WHERE date_trunc('day', end_time) == current_date
            ON CONFLICT (amenity, bump, crossing, give_way, junction, no_exit, railway, roundabout,
                         station, stop, traffic_calming, traffic_signal, turning_loop) DO NOTHING;
            
            -- Insert into twilight
            INSERT INTO twilight (
                "Twilight_ID", "Sunrise_Sunset", "Civil_Twilight", "Nautical_Twilight", "Astronomical_Twilight"
            )
            SELECT DISTINCT
                nextval('seq_twilight_id'),
                sunrise_sunset, civil_twilight, nautical_twilight, astronomical_twilight
            FROM postgres_db.public.traffic_incidents
            WHERE date_trunc('day', end_time) == current_date
            ON CONFLICT (sunrise_sunset, civil_twilight, nautical_twilight, astronomical_twilight) DO NOTHING;
            
            -- Insert into weather
            INSERT INTO weather (Weather_Condition_ID, Weather_Condition)
            SELECT DISTINCT
                nextval('seq_weather_id'),
                weather_condition
            FROM postgres_db.public.traffic_incidents
            WHERE date_trunc('day', end_time) == current_date
            ON CONFLICT (weather_condition) DO NOTHING;
            
            -- Insert into wind
            INSERT INTO wind (Wind_Direction_ID, Wind_Direction)
            SELECT DISTINCT
                nextval('seq_wind_id'),
                wind_direction
            FROM postgres_db.public.traffic_incidents
            WHERE date_trunc('day', end_time) == current_date
            ON CONFLICT (wind_direction) DO NOTHING;
            
            -- Insert into location
            INSERT INTO location (Location_ID, Street, City, County, State)
            SELECT DISTINCT
                nextval('seq_location_id'),
                street, city, county, state
            FROM postgres_db.public.traffic_incidents
            WHERE date_trunc('day', end_time) == current_date
            ON CONFLICT (street, city, county, state) DO NOTHING;

            -- Insert into accident
            INSERT INTO accident (
                Accident_ID, Severity, Start_Time, End_Time, Start_Lat, Start_Lng, End_Lat, End_Lng,
                Distance_mi, Weather_Timestamp, Temperature_F, Humidity_percent, Wind_Speed_mph,
                Precipitation_in, Visibility_mi, Location_ID, Environment_ID, Twilight_ID,
                Weather_Condition_ID, Wind_Direction_ID
            )
            SELECT
                nextval('seq_accident_id'),
                severity,
                start_time,
                end_time,
                start_lat,
                start_lng,
                end_lat,
                end_lng,
                distance_mi,
                weather_timestamp,
                temperature_f,
                humidity_percent,
                wind_speed_mph,
                precipitation_in,
                visibility_mi,
                (SELECT id FROM location WHERE street = t.street AND city = t.city AND county = t.county AND state = t.state),
                (SELECT id FROM environment WHERE amenity = t.amenity AND bump = t.bump AND crossing = t.crossing AND give_way = t.give_way
                    AND junction = t.junction AND no_exit = t.no_exit AND railway = t.railway AND roundabout = t.roundabout
                    AND station = t.station AND stop = t.stop AND traffic_calming = t.traffic_calming AND traffic_signal = t.traffic_signal
                    AND turning_loop = t.turning_loop),
                (SELECT id FROM twilight WHERE sunrise_sunset = t.sunrise_sunset AND civil_twilight = t.civil_twilight
                    AND nautical_twilight = t.nautical_twilight AND astronomical_twilight = t.astronomical_twilight),
                (SELECT id FROM weather WHERE weather_condition = t.weather_condition),
                (SELECT id FROM wind WHERE wind_direction = t.wind_direction)
            FROM postgres_db.public.traffic_incidents t
            WHERE date_trunc('day', end_time) == current_date;
            COMMIT;
            """)
            self.logger.info("ETL process completed")

        except Exception as e:
            self.logger.error(f"ETL process failed: {str(e)}")
            self.conn.execute("ROLLBACK")
            raise
        finally:
            self.close()