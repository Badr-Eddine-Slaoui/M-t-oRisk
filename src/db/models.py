from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, ForeignKey, Integer, String, Date, Boolean, Numeric
from datetime import date

class Base(DeclarativeBase):
    pass

class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    
    weather_forecasts: Mapped[list["WeatherForecast"]] = relationship("WeatherForecast", back_populates="city", cascade="all, delete-orphan")
    weather_risks: Mapped[list["WeatherRisk"]] = relationship("WeatherRisk", back_populates="city", cascade="all, delete-orphan")
