from contextlib import asynccontextmanager
from typing import Optional, Annotated
import duckdb
from fastapi import FastAPI, HTTPException, Depends
from fastapi import Response
from fastapi.params import Query
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    DUCKDB_PATH: str = ":memory:"  # Default to in-memory database if not specified
    DEBUG: bool = False  # Add debug configuration

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # Allow extra fields in environment variables
    )

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = AppConfig()
    try:
        # Ensure DuckDB connection is only initialized once
        if not DatabaseConnection.is_initialized():
            DatabaseConnection.initialize(settings.DUCKDB_PATH)
        print(f"Connected to DuckDB at {settings.DUCKDB_PATH}")
        print(f"Debug mode: {settings.DEBUG}")

        # Create any necessary tables or initialize schema here
        conn = DatabaseConnection.get_connection()
        # Example: conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        yield
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        if settings.DEBUG:
            print(f"Configuration: {settings.model_dump()}")
        raise RuntimeError(f"Failed to initialize application: {str(e)}")
    finally:
        # DatabaseConnection.close()
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
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


# noinspection SqlNoDataSourceInspection
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
                SELECT strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month, COUNT(a.Accident_ID) as count
                FROM accident a
                JOIN location l ON a.location_id = l.location_id
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
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
                SELECT strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month, weather_condition, severity, COUNT(a.Accident_ID) as count
                FROM accident a
                JOIN weather w ON a.weather_condition_id = w.weather_condition_id
                JOIN location l ON a.location_id = l.location_id
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
                GROUP BY (date_trunc('month', a.Start_Time), weather_condition, severity)
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
                SELECT strftime(date_trunc('month', a.Start_Time), '%Y-%m') as month, Start_Lat, Start_Lng, Severity
                FROM accident a JOIN location l ON a.location_id = l.location_id
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
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
        JOIN environment e ON a.environment_id = e.environment_id 
        JOIN location l ON a.location_id = l.location_id
        WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?)
        GROUP BY date_part('year', a.Start_Time), a.Severity
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
                SELECT date_part('hour', a.Start_Time) as hour, date_part('year', a.Start_Time) as year, severity, COUNT(a.Accident_ID) as count
                FROM accident a JOIN location l ON a.location_id = l.location_id
                WHERE (? IS NULL OR l.State = ?) AND (? IS NULL OR l.City = ?) 
                GROUP BY (date_part('hour', a.Start_Time), date_part('year', a.Start_Time), severity) 
                ORDER BY year, hour, severity
                """, [state, state, city, city]).df()
        return Response(res.to_json(orient="records"), media_type="application/json")
    except Exception as e:
        raise HTTPException(
            status_code=00,
            detail=f"Database error: {str(e)}"
        )