from sqlalchemy import Column, Integer, String, Float, Enum, DateTime
from sqlalchemy.sql import func
from app.db.base  import Base

class Supermarket(Base):
    __tablename__ = "supermarkets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    status = Column(Enum("green", "yellow", "red", name="supermarket_status"), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    def __repr__(self):
        return f"<Supermarket {self.name} ({self.status})>"
