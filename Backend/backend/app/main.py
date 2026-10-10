from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import diagnose, history, stores
from .db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AgriScan API", version="0.1.0", lifespan=lifespan)

# During local development the React app runs on a different port,
# so CORS needs to allow it explicitly. Tighten this before deploying.
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agri-scan-olive.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```


@app.get("/health")
def health_check():
    import os

    mock_mode = os.getenv("ALLOW_MOCK", "false").lower() == "true"

    return {
        "status": "ok",
        "mock_mode": mock_mode
    }

from fastapi.staticfiles import StaticFiles
import os

app.include_router(diagnose.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(stores.router, prefix="/api")

os.makedirs("app/uploads", exist_ok=True)
os.makedirs("app/outputs", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="app/outputs"), name="outputs")
