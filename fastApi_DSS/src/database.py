from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    Enum as SQLAlchemyEnum, DateTime
)
from sqlalchemy.ext.declarative import declarative_base

# Base for SQLAlchemy models
Base = declarative_base()


class DayNightEnum(str, Enum):
    DAY = 'Day'
    NIGHT = 'Night'


class WeatherConditionEnum(str, Enum):
    Clear = 'Clear'
    Cloudy = 'Cloudy'
    Fog = 'Fog'
    Hail = 'Hail'
    Rain = 'Rain'
    Sand = 'Sand'
    Smoke = 'Smoke'
    Snow = 'Snow'
    Thunderstorm = 'Thunderstorm'
    Tornado = 'Tornado'
    Windy = 'Windy'


class WindDirectionEnum(str, Enum):
    Calm = 'Calm'
    West = 'W'
    East = 'E'
    South = 'S'
    North = 'N'
    Northeast = 'NE'
    Southwest = 'SW'
    Southeast = 'SE'
    Northwest = 'NW'
    Variable = 'Variable'


class USStateEnum(str, Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'


# SQLAlchemy Model
class TrafficIncident(Base):
    """
    SQLAlchemy model for traffic_incidents table
    Represents a comprehensive traffic incident record
    """
    __tablename__ = 'traffic_incidents'

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Severity and Temporal Information
    severity = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    # Geospatial Information
    start_lat = Column(Float)
    start_lng = Column(Float)
    end_lat = Column(Float, nullable=True)
    end_lng = Column(Float, nullable=True)
    distance_mi = Column(Float, nullable=True)

    # Location Details
    description = Column(String, nullable=True)
    street = Column(String)
    city = Column(String)
    county = Column(String)
    state = Column(SQLAlchemyEnum(USStateEnum))

    # Weather Information
    weather_timestamp = Column(DateTime)
    temperature_f = Column(Float)
    wind_chill_f = Column(Float)
    humidity_percent = Column(Float)
    pressure_in = Column(Float)
    visibility_mi = Column(Float)
    wind_direction = Column(SQLAlchemyEnum(WindDirectionEnum))
    wind_speed_mph = Column(Float)
    precipitation_in = Column(Float)
    weather_condition = Column(SQLAlchemyEnum(WeatherConditionEnum))

    # Infrastructure and Road Conditions
    amenity = Column(Boolean)
    bump = Column(Boolean)
    crossing = Column(Boolean)
    give_way = Column(Boolean)
    junction = Column(Boolean)
    no_exit = Column(Boolean)
    railway = Column(Boolean)
    roundabout = Column(Boolean)
    station = Column(Boolean)
    stop = Column(Boolean)
    traffic_calming = Column(Boolean)
    traffic_signal = Column(Boolean)
    turning_loop = Column(Boolean)

    # Time of Day Information
    sunrise_sunset = Column(SQLAlchemyEnum(DayNightEnum))
    civil_twilight = Column(SQLAlchemyEnum(DayNightEnum))
    nautical_twilight = Column(SQLAlchemyEnum(DayNightEnum))
    astronomical_twilight = Column(SQLAlchemyEnum(DayNightEnum))


# Pydantic Model for Validation
class TrafficIncidentCreate(BaseModel):
    """
    Pydantic model for validating and serializing traffic incident data
    """
    # Severity and Temporal Information
    severity: int = Field(None, ge=1, le=4)
    start_time: datetime
    end_time: Optional[datetime] = None

    # Geospatial Information
    start_lat: Optional[float] = Field(None, ge=-90, le=90)
    start_lng: Optional[float] = Field(None, ge=-180, le=180)
    end_lat: Optional[float] = Field(None, ge=-90, le=90)
    end_lng: Optional[float] = Field(None, ge=-180, le=180)
    distance_mi: Optional[float] = Field(None, ge=0)

    # Location Details
    description: Optional[str] = Field(None, max_length=1000)
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    state: Optional[USStateEnum] = None

    # Weather Information
    weather_timestamp: Optional[datetime] = None
    temperature_f: Optional[float] = Field(None, ge=-50, le=150)
    wind_chill_f: Optional[float] = Field(None, ge=-50, le=150)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    pressure_in: Optional[float] = Field(None, ge=0, le=50)
    visibility_mi: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[WindDirectionEnum] = None
    wind_speed_mph: Optional[float] = Field(None, ge=0)
    precipitation_in: Optional[float] = Field(None, ge=0)
    weather_condition: Optional[WeatherConditionEnum] = None

    # Infrastructure and Road Conditions
    amenity: Optional[bool] = None
    bump: Optional[bool] = None
    crossing: Optional[bool] = None
    give_way: Optional[bool] = None
    junction: Optional[bool] = None
    no_exit: Optional[bool] = None
    railway: Optional[bool] = None
    roundabout: Optional[bool] = None
    station: Optional[bool] = None
    stop: Optional[bool] = None
    traffic_calming: Optional[bool] = None
    traffic_signal: Optional[bool] = None
    turning_loop: Optional[bool] = None

    # Time of Day Information
    sunrise_sunset: Optional[DayNightEnum] = None
    civil_twilight: Optional[DayNightEnum] = None
    nautical_twilight: Optional[DayNightEnum] = None
    astronomical_twilight: Optional[DayNightEnum] = None

    # Custom Validators
    @classmethod
    @field_validator('start_time')
    def validate_start_time(cls, v):
        if v is None:
            raise ValueError("Start time must be provided")
        return v

    @classmethod
    @field_validator('end_time')
    def validate_end_time(cls, v, values):
        if v is not None and 'start_time' in values and v < values['start_time']:
            raise ValueError("End time must be after start time")
        return v

    class Config:
        # Allow arbitrary types for enum-like string inputs
        use_enum_values = True
        # Example of additional JSON Schema validation
        json_schema_extra = {
            "examples": [
                {
                    "start_time": "2023-06-15T10:30:00",
                    "severity": "2",
                    "state": "CA",
                    "weather_condition": "Clear"
                }
            ]
        }