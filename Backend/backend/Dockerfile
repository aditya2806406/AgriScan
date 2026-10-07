FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# The backend expects the ml/ and data/ directories as siblings of backend/
# when run outside Docker. In a container, mount or copy them explicitly —
# see docker-compose.yml at the project root for the working setup.

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
