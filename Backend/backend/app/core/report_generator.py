import os
from pathlib import Path
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, KeepTogether, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

from ..db.models import Scan
from ..core.treatment_lookup import get_treatment

BASE_DIR = Path(__file__).resolve().parent.parent

def generate_report(scan: Scan, predictions: list, gradcam_url: str = None) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    
    # Custom styles matching AgriScan's theme
    title_style = ParagraphStyle(
        'AgriScanTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a2e22'), # Dark forest green
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'AgriScanSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#666666'),
        spaceAfter=24
    )
    
    heading_style = ParagraphStyle(
        'AgriScanHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#1a2e22'),
        spaceBefore=16,
        spaceAfter=8,
        borderPadding=4,
        borderColor=HexColor('#1a2e22'),
        borderWidth=1
    )
    
    normal_style = styles["Normal"]
    normal_style.spaceAfter = 8
    
    alert_style = ParagraphStyle(
        'AgriScanAlert',
        parent=styles['Normal'],
        textColor=HexColor('#7f1d1d'), # Brick red
        fontName='Helvetica-Bold',
        spaceAfter=12
    )

    story = []

    # --- Header ---
    story.append(Paragraph("AGRISCAN", title_style))
    story.append(Paragraph("Crop Disease Detection Report", subtitle_style))
    
    date_str = scan.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    story.append(Paragraph(f"<b>Date / Time:</b> {date_str}", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    # --- Image Handling ---
    # Safely load the original image if available
    if scan.image_path and str(scan.image_path).startswith("/uploads/"):
        filename = scan.image_path.split("/")[-1]
        img_path = BASE_DIR / "uploads" / filename
        if img_path.exists():
            story.append(Paragraph("SCAN IMAGE", heading_style))
            try:
                # Keep aspect ratio, max width 4 inches
                img = RLImage(str(img_path))
                img.drawWidth = 4 * inch
                img.drawHeight = img.drawWidth * (img.imageHeight / img.imageWidth)
                story.append(img)
                story.append(Spacer(1, 0.2 * inch))
            except Exception:
                story.append(Paragraph("<i>Image unavailable</i>", normal_style))

    # --- Detection Result ---
    story.append(Paragraph("DETECTION RESULT", heading_style))
    
    if scan.prediction_status == "image_quality_failed":
        story.append(Paragraph("<b>Prediction Status:</b> Image quality check failed", alert_style))
        story.append(Paragraph("No disease diagnosis could be performed.", normal_style))
    else:
        # High or low confidence
        status_text = "High-confidence prediction"
        if scan.is_low_confidence:
            status_text = "Possible match — low confidence"
            
        story.append(Paragraph(f"<b>Crop:</b> {scan.predicted_crop or 'Unknown'}", normal_style))
        story.append(Paragraph(f"<b>Possible Disease / Condition:</b> {scan.predicted_disease or 'Unknown'}", normal_style))
        if scan.confidence is not None:
            story.append(Paragraph(f"<b>Model Confidence:</b> {scan.confidence * 100:.2f}%", normal_style))
        story.append(Paragraph(f"<b>Prediction Status:</b> {status_text}", normal_style))
        
        # --- Top Predictions ---
        if predictions:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>Top Predictions:</b>", normal_style))
            for i, p in enumerate(predictions, 1):
                raw_disease = p.get("disease", "Unknown")
                conf = p.get("confidence", 0)
                
                parts = raw_disease.split("___") if "___" in raw_disease else [raw_disease, raw_disease]
                crop_name = parts[0].replace("_", " ")
                cond_name = parts[1].replace("_", " ") if len(parts) > 1 else parts[0]
                
                story.append(Paragraph(f"{i}. {crop_name} — {cond_name} ({conf:.2f}%)", normal_style))
        
        story.append(Spacer(1, 0.2 * inch))

        # --- Grad-CAM ---
        if gradcam_url and gradcam_url.startswith("/outputs/") and ".." not in gradcam_url:
            gc_filename = gradcam_url.split("/")[-1]
            gc_path = BASE_DIR / "outputs" / gc_filename
            if gc_path.exists():
                story.append(Paragraph("MODEL EXPLANATION", heading_style))
                try:
                    gc_img = RLImage(str(gc_path))
                    gc_img.drawWidth = 3 * inch
                    gc_img.drawHeight = gc_img.drawWidth * (gc_img.imageHeight / gc_img.imageWidth)
                    story.append(gc_img)
                    story.append(Paragraph("<i>Grad-CAM highlights image regions that contributed most to the model's prediction.</i>", normal_style))
                    story.append(Spacer(1, 0.2 * inch))
                except Exception:
                    pass

        # --- Low Confidence Warning ---
        if scan.is_low_confidence:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>Possible Match</b>", alert_style))
            story.append(Paragraph("The model confidence is below the application's treatment recommendation threshold. The result should be treated as a possible match rather than a confirmed diagnosis.", normal_style))
            story.append(Paragraph("Treatment recommendations are withheld.", normal_style))

        # --- Treatment ---
        elif scan.disease:
            treatment_info = get_treatment(scan.disease)
            if treatment_info:
                story.append(PageBreak())
                story.append(Paragraph("TREATMENT", heading_style))
                
                def add_list_section(title, items):
                    if items:
                        story.append(Paragraph(f"<b>{title}:</b>", normal_style))
                        for item in items:
                            story.append(Paragraph(f"• {item}", normal_style))
                        story.append(Spacer(1, 0.1 * inch))

                add_list_section("Symptoms", treatment_info.get("symptoms", []))
                add_list_section("Organic Management", treatment_info.get("organic_management", []))
                add_list_section("Chemical Management", treatment_info.get("chemical_management", []))
                add_list_section("Prevention", treatment_info.get("prevention", []))
                
                caution = treatment_info.get("caution")
                if caution:
                    story.append(Paragraph(f"<b>Caution:</b> {caution}", alert_style))
                    story.append(Spacer(1, 0.1 * inch))
                
                add_list_section("Sources", treatment_info.get("sources", []))

    # --- Responsible AI Note ---
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Important Note", heading_style))
    story.append(Paragraph(
        "AgriScan provides AI-assisted crop image analysis and should not be treated as a definitive agricultural diagnosis. "
        "Model predictions are limited to the conditions represented in the trained model and may be affected by image quality, "
        "lighting, background, and real-world field conditions. Confirm important crop-health decisions with a qualified "
        "agricultural professional or local agricultural guidance.", normal_style
    ))
    
    # --- Model Info ---
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Model:</b> MobileNetV2", normal_style))
    story.append(Paragraph("<b>Training dataset:</b> PlantVillage", normal_style))
    story.append(Paragraph("<b>Supported classes:</b> 38", normal_style))

    # --- Footer ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#666666'))
        canvas.drawString(inch, 0.5 * inch, "AgriScan — AI-assisted crop health analysis")
        canvas.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    
    buffer.seek(0)
    return buffer
