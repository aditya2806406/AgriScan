from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

class Treatment(BaseModel):
    disease: str
    symptoms: List[str]
    organic_management: List[str]
    chemical_management: List[str]
    prevention: List[str]
    caution: str
    sources: List[str]


class DiagnosisResponse(BaseModel):
    filename: str
    image_quality: dict
    prediction_status: str
    disease: Optional[str] = None
    display_name: Optional[str] = None
    confidence: Optional[float] = None
    predictions: Optional[List[dict]] = None
    gradcam: Optional[str] = None
    is_low_confidence: bool = False
    treatment: Optional[Treatment] = None
    scan_id: Optional[int] = None

class ReportRequest(BaseModel):
    scan_id: int
    predictions: Optional[List[dict]] = None
    gradcam_url: Optional[str] = None

class ScanHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disease: Optional[str]
    confidence: Optional[float]
    prediction_status: str
    created_at: datetime
