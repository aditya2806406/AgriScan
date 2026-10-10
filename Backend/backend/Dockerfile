FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV MODEL_PATH=/app/ml/models/mobilenetv2_test.pth
ENV TREATMENTS_PATH=/app/data/treatments.json

COPY Backend/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/backend/app ./app
COPY Backend/backend/ml ./ml
COPY Backend/data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
