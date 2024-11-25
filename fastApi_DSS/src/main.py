import logging
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta
from typing import Optional, Annotated, Dict
import duckdb
import pytz
from fastapi import FastAPI, HTTPException, Depends
from fastapi import Response
from fastapi.params import Query
from pydantic_settings import BaseSettings, SettingsConfigDict
import asyncio

from orchestrator import DuckDBPostgresETL


class AppConfig(BaseSettings):
    DUCKDB_PATH: str = ":memory:"  # Default to in-memory database if not specified
    DEBUG: bool = False  # Add debug configuration

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    ETL_RUN_TIME: str = "23:00"
    ETL_TIMEZONE: str = "Asia/Ho_Chi_Minh"
    SOURCE_TABLE: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="allow"  # Allow extra fields in environment variables
    )

    @property
    def postgres_config(self) -> Dict[str, str]:
        return {
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
        }

class DatabaseConnection:
    _instance: Optional[duckdb.DuckDBPyConnection] = None

    @classmethod
    def get_connection(cls) -> duckdb.DuckDBPyConnection:
        if cls._instance is None:
            raise HTTPException(
                status_code=500,
                detail="Database connection is not initialized."
            )
        return cls._instance

    @classmethod
    def initialize(cls, path: str) -> None:
        if cls._instance is not None:
            cls.close()
        cls._instance = duckdb.connect(path)

    @classmethod
    def close(cls) -> None:
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    @classmethod
    def is_initialized(cls) -> bool:
        return cls._instance is not None


async def get_db() -> duckdb.DuckDBPyConnection:
    """Dependency for getting database connection"""
    conn = DatabaseConnection.get_connection()
    if not conn:
        raise HTTPException(
            status_code=500,
            detail="Database connection is not available"
        )
    return conn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../etl_log.log'),
        logging.StreamHandler()
    ]
)


class ETLManager:
    def __init__(self, settings: AppConfig):
        self.settings = settings
        self.etl_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)
        self.etl = DuckDBPostgresETL(
            settings.DUCKDB_PATH,
            settings.postgres_config,
            self.logger)

        # Parse ETL run time
        run_time = datetime.strptime(settings.ETL_RUN_TIME, "%H:%M").time()
        self.run_time = time(run_time.hour, run_time.minute)
        self.timezone = pytz.timezone(settings.ETL_TIMEZONE)

    async def schedule_next_run(self) -> None:
        """Calculate and wait until the next run time"""
        now = datetime.now(self.timezone)
        target = datetime.combine(now.date(), self.run_time)
        target = self.timezone.localize(target)

        # If today's run time has passed, schedule for tomorrow
        if now >= target:
            target = target + timedelta(days=1)

        # Calculate seconds until next run
        delay = (target - now).total_seconds()
        await asyncio.sleep(delay)

    async def run_etl_loop(self) -> None:
        """
        Run ETL process in a loop at scheduled times
        source_table: Postgres table to extract data from
        target_table: DuckDB table to load data into
        """
        table_configs = [
            {"source_table": {self.settings.SOURCE_TABLE}, "target_table": "users_daily"},
            # Add more table configurations as needed
        ]

        while True:
            try:
                # DO NOT ENABLE ANY LINE. THE ORCHESTRATOR IS UNSTABLE.
                print("ETL loop")
                # self.etl.setup_connection()
                # await self.schedule_next_run()
                # Run ETL process
                # self.logger.info("Starting scheduled ETL run")
                # self.etl.run_daily_etl(table_configs)
                # self.logger.info("Completed scheduled ETL run")
            except Exception as e:
                self.logger.error(f"Error in ETL loop: {str(e)}")
                if self.settings.DEBUG:
                    self.logger.exception("Detailed error information:")

            # Even if there's an error, continue the loop
            await asyncio.sleep(60000)  # Wait a minute before checking schedule again

    def start(self) -> None:
        """Start the ETL background task"""
        if self.etl_task is None or self.etl_task.done():
            self.etl_task = asyncio.create_task(self.run_etl_loop())
            self.logger.info("ETL background task started")

    def stop(self) -> None:
        """Stop the ETL background task"""
        if self.etl_task and not self.etl_task.done():
            self.etl_task.cancel()
            self.logger.info("ETL background task stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = AppConfig()
    etl_manager = None
    try:
        # Ensure DuckDB connection is only initialized once
        if not DatabaseConnection.is_initialized():
            DatabaseConnection.initialize(settings.DUCKDB_PATH)
        print(f"Connected to DuckDB at {settings.DUCKDB_PATH}")
        print(f"Debug mode: {settings.DEBUG}")

        # Initialize and start ETL manager
        etl_manager = ETLManager(settings)
        etl_manager.start()

        yield
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        if settings.DEBUG:
            print(f"Configuration: {settings.model_dump()}")
        raise RuntimeError(f"Failed to initialize application: {str(e)}")
    finally:
        if etl_manager:
            etl_manager.stop()
        DatabaseConnection.close()
        print("Closed DuckDB connection")


# FastAPI application
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# noinspection SqlDialectInspection
@app.get("/health")
async def health_check(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Health check endpoint that verifies database connection"""
    try:
        # Simple query to verify database connection
        # res = db.execute("SELECT max(accident_id) FROM accident").df()
        # return Response(res.to_json(orient="records"), media_type="application/json")
        db.execute("SELECT 1").df()
        # db.execute("""
        #         DELETE FROM accident WHERE accident_id >= 7728400;
        # """)
        # db.execute("""
        # CREATE OR REPLACE SEQUENCE seq_environment_id START 349;
        # CREATE OR REPLACE SEQUENCE seq_location_id START 624778;
        # CREATE OR REPLACE SEQUENCE seq_weather_id START 13;
        # CREATE OR REPLACE SEQUENCE seq_accident_id START 7728400;
        # CREATE OR REPLACE SEQUENCE seq_twilight_id START 12;
        # CREATE OR REPLACE SEQUENCE seq_wind_id START 12;
        # """)
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


# noinspection SqlDialectInspection
@app.get("/chart/1")
async def get_chart_data_1(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )

    try:
        res = db.execute("""
                SELECT strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month, Severity, COUNT(a.Accident_ID) as count
                FROM accident a
                JOIN location l ON a.Location_ID = l.Location_ID
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
                GROUP BY month, a.Severity
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

# noinspection SqlNoDataSourceInspection
# noinspection SqlDialectInspection
@app.get("/chart/2")
async def get_chart_data_2(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )

    try:
        res = db.execute("""
                SELECT strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month, Weather_Condition, Severity, COUNT(a.Accident_ID) as count
                FROM accident a
                JOIN weather w ON a.Weather_Condition_ID = w.Weather_Condition_ID
                JOIN location l ON a.Location_ID = l.Location_ID
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
                GROUP BY month, Weather_Condition, Severity
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


# noinspection SqlDialectInspection
@app.get("/chart/3")
async def get_chart_data_34(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )

    try:
        res = db.execute("""
                SELECT 
                    strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month,
                    ROUND(Start_Lat, 1) as grid_lat, 
                    ROUND(Start_Lng, 1) as grid_lng, 
                    COUNT(*) as accident_count
                FROM accident a 
                JOIN location l ON a.Location_ID = l.Location_ID
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
                GROUP BY month, grid_lat, grid_lng
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=00,
            detail=f"Database error: {str(e)}"
        )

# noinspection SqlDialectInspection
@app.get("/chart/4")
async def get_chart_data_34(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )

    try:
        res = db.execute("""
                SELECT 
                    strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month,
                    ROUND(Start_Lat, 1) as grid_lat, 
                    ROUND(Start_Lng, 1) as grid_lng, 
                    Severity,
                    COUNT(*) as accident_count
                FROM accident a 
                JOIN location l ON a.Location_ID = l.Location_ID
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
                GROUP BY month, grid_lat, grid_lng, Severity
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=00,
            detail=f"Database error: {str(e)}"
        )

# noinspection SqlDialectInspection
@app.get("/chart/5")
async def get_chart_data_5(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )

    try:
        res = db.execute("""
        SELECT 
            date_part('year', a.Start_Time) AS year, 
            a.Severity,
            COUNT(CASE WHEN e.Amenity THEN 1 END) AS Amenity, 
            COUNT(CASE WHEN e.Bump THEN 1 END) AS Bump, 
            COUNT(CASE WHEN e.Crossing THEN 1 END) AS Crossing, 
            COUNT(CASE WHEN e.Give_Way THEN 1 END) AS Give_Way, 
            COUNT(CASE WHEN e.Junction THEN 1 END) AS Junction, 
            COUNT(CASE WHEN e.No_Exit THEN 1 END) AS No_Exit, 
            COUNT(CASE WHEN e.Railway THEN 1 END) AS Railway, 
            COUNT(CASE WHEN e.Roundabout THEN 1 END) AS Roundabout, 
            COUNT(CASE WHEN e.Station THEN 1 END) AS Station, 
            COUNT(CASE WHEN e.Stop THEN 1 END) AS Stop, 
            COUNT(CASE WHEN e.Traffic_Calming THEN 1 END) AS Traffic_Calming, 
            COUNT(CASE WHEN e.Traffic_Signal THEN 1 END) AS Traffic_Signal, 
            COUNT(CASE WHEN e.Turning_Loop THEN 1 END) AS Turning_Loop
        FROM accident a 
        JOIN environment e ON a.Environment_ID = e.Environment_ID 
        JOIN location l ON a.Location_ID = l.Location_ID
        WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
        GROUP BY year, a.Severity
        ORDER BY year, a.Severity;
        """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

# noinspection SqlDialectInspection
@app.get("/chart/6")
async def get_chart_data_6(state: Annotated[Optional[str], Query(alias="state")] = None,
                           city: Annotated[Optional[str], Query(alias="city")] = None,
                           db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if city and not state:
        raise HTTPException(
            status_code=400,
            detail="State must be provided if City is specified."
        )
    try:
        res = db.execute("""
                SELECT date_part('hour', a.Start_Time) as hour, date_part('year', a.Start_Time) as year, Severity, COUNT(a.Accident_ID) as count
                FROM accident a JOIN location l ON a.Location_ID = l.Location_ID
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?) 
                GROUP BY hour, year, Severity 
                ORDER BY year, hour, Severity
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=00,
            detail=f"Database error: {str(e)}"
        )