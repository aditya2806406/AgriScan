from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
import asyncio
from sqlalchemy.orm import Session

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "ml" / "src"))
from predict import predict_image_bytes

from ..core.treatment_lookup import get_treatment
from ..db.models import Scan
from ..db.session import get_db
from fastapi.responses import StreamingResponse
from ..schemas import DiagnosisResponse, Treatment, ReportRequest
from ..core.report_generator import generate_report

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


import os

prediction_semaphore = asyncio.Semaphore(1)

@router.post("/predict", response_model=DiagnosisResponse)
async def predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Please upload a JPEG, PNG, or WebP image.")

    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")


    import uuid
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = Path("app/uploads") / safe_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(image_bytes)

    image_reference = f"/uploads/{safe_filename}"

    try:
        await asyncio.wait_for(prediction_semaphore.acquire(), timeout=0.05)
    except TimeoutError:
        raise HTTPException(status_code=503, detail="Server is currently busy processing another image. Please try again in a moment.")

    task = asyncio.create_task(run_in_threadpool(predict_image_bytes, image_bytes))
    try:
        quality_info, results, heatmap_url = await asyncio.shield(task)
    except asyncio.CancelledError:
        # If client disconnects, thread is still running. Release semaphore only after thread finishes.
        async def release_later():
            try:
                await task
            except Exception:
                pass
            finally:
                prediction_semaphore.release()
        asyncio.create_task(release_later())
        raise
    except Exception:
        prediction_semaphore.release()
        raise
    else:
        prediction_semaphore.release()

    if not quality_info["acceptable"]:
        if quality_info.get("is_malformed"):
            raise HTTPException(status_code=400, detail=quality_info["issues"][0])

        # Log failed scan
        scan = Scan(
            disease=None,
            confidence=None,
            prediction_status="image_quality_failed",
            image_quality_status="failed",
            image_path=image_reference
        )
        db.add(scan)
        db.commit()

        return DiagnosisResponse(
            filename=file.filename,
            image_quality=quality_info,
            prediction_status="image_quality_failed",
            scan_id=scan.id
        )

    top_prediction = results[0]
    disease = top_prediction["disease"]
    confidence = top_prediction["confidence"] / 100.0  # normalize to 0-1 for frontend

    threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    is_low_confidence = confidence < threshold
    prediction_status = "low_confidence" if is_low_confidence else "high_confidence"

    # parse crop and condition
    crop = "Unknown"
    condition = disease
    if "___" in disease:
        parts = disease.split("___")
        crop = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ")

    # Log the scan to history
    scan = Scan(
        disease=disease,
        predicted_crop=crop,
        predicted_disease=condition,
        confidence=confidence,
        is_low_confidence=is_low_confidence,
        prediction_status=prediction_status,
        image_quality_status="acceptable",
        image_path=image_reference
    )
    db.add(scan)
    db.commit()

    treatment_info = get_treatment(disease)
    treatment_payload = None

    if not is_low_confidence:
        treatment_payload = Treatment(
            disease=treatment_info.get("disease", disease),
            symptoms=treatment_info.get("symptoms", []),
            organic_management=treatment_info.get("organic_management", []),
            chemical_management=treatment_info.get("chemical_management", []),
            prevention=treatment_info.get("prevention", []),
            caution=treatment_info.get("caution", ""),
            sources=treatment_info.get("sources", [])
        )

    return DiagnosisResponse(
        filename=file.filename,
        image_quality=quality_info,
        prediction_status=prediction_status,
        disease=disease,
        display_name=treatment_info.get("disease", disease),
        confidence=confidence,
        predictions=results,
        gradcam=heatmap_url,
        is_low_confidence=is_low_confidence,
        treatment=treatment_payload,
        scan_id=scan.id
    )

@router.post("/report")
def download_report(request: ReportRequest, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == request.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    pdf_buffer = generate_report(scan, request.predictions or [], request.gradcam_url)

    # Generate safe filename based on result
    date_str = scan.created_at.strftime("%Y-%m-%d")
    filename = "AgriScan_Report"
    if scan.predicted_crop and scan.predicted_disease:
        safe_crop = "".join(c for c in scan.predicted_crop if c.isalnum() or c in (" ", "_")).replace(" ", "_")
        safe_cond = "".join(c for c in scan.predicted_disease if c.isalnum() or c in (" ", "_")).replace(" ", "_")
        filename += f"_{safe_crop}_{safe_cond}"
    filename += f"_{date_str}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/supported-classes")
def get_supported_classes():
    from predict import get_classes

    return {
        "classes": get_classes()
    }
