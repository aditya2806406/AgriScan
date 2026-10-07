import urllib.request
import urllib.parse
import json
import os

from io import BytesIO

# 1. Post to predict
print("Uploading image...")
import uuid
boundary = uuid.uuid4().hex
file_path = "ml/data/color/Apple___healthy/0055dd26-23a7-4415-ac61-e0b44ebfaf80___RS_HL 5672.JPG"

with open(file_path, "rb") as f:
    img_data = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
    f"Content-Type: image/jpeg\r\n\r\n"
).encode('utf-8') + img_data + f"\r\n--{boundary}--\r\n".encode('utf-8')

req = urllib.request.Request("http://localhost:8000/api/predict", data=body, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Predict response:", data["prediction_status"])
        scan_id = data["scan_id"]
        
        # 2. Post to report
        print("Generating report for scan_id:", scan_id)
        report_payload = {
            "scan_id": scan_id,
            "predictions": data.get("predictions", []),
            "gradcam_url": data.get("gradcam")
        }
        
        req_report = urllib.request.Request("http://localhost:8000/api/report", data=json.dumps(report_payload).encode('utf-8'), method="POST")
        req_report.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(req_report) as rep_res:
            pdf_data = rep_res.read()
            with open("test_report.pdf", "wb") as pf:
                pf.write(pdf_data)
            print("Successfully saved test_report.pdf")
            
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
