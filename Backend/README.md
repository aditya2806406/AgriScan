# AgriScan — Backend Bundle

This is the **server side** of AgriScan: the API, the ML code, and the data
it depends on. There is no website code in here — see the separate
`agriscan-frontend` package for that.

## Folder guide

```
backend/    ← the actual API server (FastAPI). Run this to serve requests.
ml/         ← model training code (transfer learning + Grad-CAM) and where
              a trained model file gets saved. The backend imports directly
              from ml/src/ at runtime — that's why it's bundled here, not
              treated as a separate project.
data/       ← treatments.json — the curated disease → treatment lookup data
              the backend reads from.
```

## To run it

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

It'll run in **mock mode** by default (no trained model needed yet) — see
`backend/README` notes inside `app/core/model_loader.py` for how mock mode
works, and the full project README (in the combined zip) for the complete
walkthrough including training the real model later.

Test it's working:
```bash
curl http://localhost:8000/health
```
