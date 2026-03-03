from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Stint(Base):
    __tablename__ = "stints"
    stint_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    stint_number = Column(Integer, nullable=False)
    compound = Column(String(20))
    start_lap = Column(Integer)
    end_lap = Column(Integer)

    @property
    def length(self):
        if self.start_lap and self.end_lap:
            return self.end_lap - self.start_lap + 1
        return None

    race = relationship("Race", back_populates="stints")
    driver = relationship("Driver", back_populates="stints")
