from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Lap(Base):
    __tablename__ = "laps"
    lap_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    lap_number = Column(Integer, nullable=False)

    # Times in milliseconds (NULL = deleted/invalid lap)
    lap_time_ms = Column(Float)
    s1_ms = Column(Float)
    s2_ms = Column(Float)
    s3_ms = Column(Float)

    compound = Column(String(20))       # SOFT, MEDIUM, HARD, INTER, WET
    tyre_life = Column(Integer)         # laps on current tyre set
    is_personal_best = Column(Boolean, default=False)
    track_status = Column(String(10))   # 1=green, 2=yellow, 4=SC, 6=VSC, 7=red

    race = relationship("Race", back_populates="laps")
    driver = relationship("Driver", back_populates="laps")
