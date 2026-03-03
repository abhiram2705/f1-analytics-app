from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class RaceResult(Base):
    __tablename__ = "race_results"
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    position = Column(Integer)
    grid = Column(Integer)
    points = Column(Float, default=0)
    status = Column(String(50))          # "Finished", "+1 Lap", "DNF", etc.
    fastest_lap_rank = Column(Integer)
    fastest_lap_time_ms = Column(Float)

    race = relationship("Race", back_populates="results")
    driver = relationship("Driver", back_populates="results")


class DriverStanding(Base):
    __tablename__ = "driver_standings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, ForeignKey("seasons.year"), nullable=False)
    round = Column(Integer, nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    position = Column(Integer)
    points = Column(Float, default=0)
    wins = Column(Integer, default=0)

    driver = relationship("Driver", back_populates="standings")


class ConstructorStanding(Base):
    __tablename__ = "constructor_standings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, ForeignKey("seasons.year"), nullable=False)
    round = Column(Integer, nullable=False)
    team_id = Column(String(50), ForeignKey("constructors.team_id"), nullable=False)
    position = Column(Integer)
    points = Column(Float, default=0)
    wins = Column(Integer, default=0)

    constructor = relationship("Constructor", back_populates="standings")
