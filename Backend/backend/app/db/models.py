from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def _utcnow():
    return datetime.now(timezone.utc)

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=True)
    predicted_crop = Column(String, nullable=True)
    predicted_disease = Column(String, nullable=True)
    disease = Column(String, nullable=True) # nullable for quality fails
    confidence = Column(Float, nullable=True) # nullable for quality fails
    is_low_confidence = Column(Boolean, nullable=True)
    image_quality_status = Column(String, nullable=True)
    prediction_status = Column(String, nullable=False, default="unknown")
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
