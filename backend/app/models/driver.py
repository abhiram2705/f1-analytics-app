from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(String(50), primary_key=True)  # e.g. "verstappen"
    code = Column(String(3))                            # e.g. "VER"
    full_name = Column(String(100), nullable=False)
    number = Column(Integer)
    nationality = Column(String(50))
    team_id = Column(String(50), ForeignKey("constructors.team_id"))

    constructor = relationship("Constructor", back_populates="drivers")
    laps = relationship("Lap", back_populates="driver")
    stints = relationship("Stint", back_populates="driver")
    pit_stops = relationship("PitStop", back_populates="driver")
    results = relationship("RaceResult", back_populates="driver")
    standings = relationship("DriverStanding", back_populates="driver")
