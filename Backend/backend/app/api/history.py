from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.models import Scan
from ..db.session import get_db
from ..schemas import ScanHistoryItem

router = APIRouter()


@router.get("/history", response_model=List[ScanHistoryItem])
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(limit).all()
    return scans
