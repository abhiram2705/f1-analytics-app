from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Season(Base):
    __tablename__ = "seasons"
    year = Column(Integer, primary_key=True)
    races = relationship("Race", back_populates="season_rel")


class Circuit(Base):
    __tablename__ = "circuits"
    circuit_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    city = Column(String(50))
    races = relationship("Race", back_populates="circuit")


class Constructor(Base):
    __tablename__ = "constructors"
    team_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50))
    drivers = relationship("Driver", back_populates="constructor")
    standings = relationship("ConstructorStanding", back_populates="constructor")


class Race(Base):
    __tablename__ = "races"
    race_id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, ForeignKey("seasons.year"), nullable=False)
    round = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    circuit_id = Column(String(50), ForeignKey("circuits.circuit_id"))
    date = Column(Date)

    season_rel = relationship("Season", back_populates="races")
    circuit = relationship("Circuit", back_populates="races")
    laps = relationship("Lap", back_populates="race")
    stints = relationship("Stint", back_populates="race")
    pit_stops = relationship("PitStop", back_populates="race")
    results = relationship("RaceResult", back_populates="race")
