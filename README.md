# AgriScan 🌱
### AI-Powered Crop Disease Detection, Explainability, Treatment Guidance & Agricultural Store Locator

AgriScan is a full-stack crop-health assistance platform that combines deep-learning-based leaf disease classification with visual explanations, treatment guidance, diagnosis history, PDF reports, and an interactive map for finding nearby agricultural supply stores. The goal is to make crop-health information easier to access through a single, user-friendly web application.

**Live application:** https://agri-scan-olive.vercel.app/  
**Backend API:** https://agriscan-6up4.onrender.com  
**GitHub repository:** https://github.com/aditya2806406/AgriScan

---

## Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Application Workflow](#-application-workflow)
4. [Technology Stack](#-technology-stack)
5. [System Architecture](#-system-architecture)
6. [Repository Structure](#-repository-structure)
7. [Crop Classes Supported](#-crop-classes-supported)
8. [AI Model and Prediction Pipeline](#-ai-model-and-prediction-pipeline)
9. [Grad-CAM Explainability](#-grad-cam-explainability)
10. [Treatment Recommendation System](#-treatment-recommendation-system)
11. [Nearby Agricultural Store Locator](#-nearby-agricultural-store-locator)
12. [Diagnosis History](#-diagnosis-history)
13. [PDF Diagnosis Reports](#-pdf-diagnosis-reports)
14. [Backend API](#-backend-api)
15. [Installation and Local Development](#-installation-and-local-development)
16. [Environment Configuration](#-environment-configuration)
17. [Deployment](#-deployment)
18. [Testing](#-testing)
19. [Troubleshooting](#-troubleshooting)
20. [Security, Privacy and Responsible Use](#-security-privacy-and-responsible-use)
21. [Limitations](#-limitations)
22. [Future Enhancements](#-future-enhancements)
23. [Contributing](#-contributing)
24. [License](#-license)

---

## 🌿 Project Overview

Plant diseases can affect crop health, productivity, and farmers' livelihoods. Identifying a disease early can help people investigate symptoms and seek suitable advice sooner. AgriScan provides a digital starting point: users upload a photograph of a crop leaf, the backend processes it with a trained image-classification model, and the application presents the predicted class and supporting information.

AgriScan brings the following capabilities together:

- **AI-based diagnosis:** classify a leaf image into one of the model's supported crop/disease categories.
- **Confidence information:** communicate how strongly the model favours its predicted category.
- **Visual explainability:** generate a Grad-CAM heatmap to highlight image regions associated with a prediction.
- **Treatment guidance:** look up relevant information from the project's curated treatment data.
- **Diagnosis history:** retain and revisit previous diagnosis records.
- **PDF reports:** create a portable report of diagnosis information.
- **Agricultural store locator:** explore nearby agricultural supply stores on an interactive map using geographic data from OpenStreetMap.

AgriScan is an educational and decision-support project. It does not replace laboratory testing, field inspection, or advice from a qualified agricultural professional.

## ✨ Key Features

### 1. Crop Leaf Image Upload
- Upload a crop-leaf photograph through the web interface.
- Send the image to the backend for processing.
- Validate and preprocess the image before model inference.
- Handle unreadable or unsupported images with an appropriate error response.

### 2. AI Crop Disease Classification
- Uses a PyTorch MobileNetV2 image-classification model.
- Predicts a supported crop/disease label from the uploaded image.
- Returns a predicted label and confidence information for the user interface.
- Supports healthy and diseased categories represented in the model's training labels.

### 3. Confidence and Image Quality
- Presents the model's confidence alongside its prediction.
- Supports low-confidence handling and image-quality checks where configured in the application.
- Encourages users to capture a clear, well-lit image showing the affected leaf.
- Helps prevent an uncertain prediction from being interpreted as a guaranteed diagnosis.

### 4. Grad-CAM Visual Explanation
- Produces a class-activation heatmap for the prediction.
- Helps users inspect which parts of the image influenced the model.
- Adds interpretability to the classification result.

### 5. Treatment Guidance
- Maps the predicted class to relevant information in the treatment data.
- Presents guidance associated with the predicted crop/disease category when a matching entry is available.
- Keeps treatment information separate from the model's classification step.

### 6. Diagnosis History
- Provides backend support for storing and retrieving diagnosis records.
- Makes it possible to revisit prior results rather than relying only on the current session.
- Uses the configured SQLAlchemy database layer.

### 7. PDF Reports
- Generates downloadable diagnosis reports using ReportLab.
- Provides a portable summary of diagnosis information for later reference.

### 8. Nearby Agricultural Store Locator 🗺️
- Displays geographic information on an interactive map.
- Uses a user's current location when permission is granted, or coordinates supplied by the interface.
- Queries nearby agricultural-store features through the backend's OpenStreetMap/Overpass integration.
- Calculates straight-line distance where supported.
- Presents nearby results on the map and in the associated results interface.
- Can link users to mapping directions when that action is enabled in the frontend.

### 9. Web API and Deployment
- FastAPI backend with interactive API documentation.
- React frontend deployed independently from the API.
- Backend deployment configured for Render.
- Frontend deployment configured for Vercel.

---

## 🔄 Application Workflow

```text
User opens AgriScan
        |
        v
Select a leaf image
        |
        v
Frontend submits image to FastAPI
        |
        v
Validate and preprocess image
        |
        v
MobileNetV2 performs inference
        |
        v
Predicted class + confidence
        |
        +----------------------+
        |                      |
        v                      v
Grad-CAM explanation     Treatment data lookup
        |                      |
        +-----------+----------+
                    |
                    v
             Diagnosis results
                    |
          +---------+----------+
          |         |          |
          v         v          v
       History    PDF report  Store locator
                              |
                              v
                     Location coordinates
                              |
                              v
                    Backend nearby-store API
                              |
                              v
                    OpenStreetMap / Overpass
                              |
                              v
                    Map markers and store list
```

## 🧰 Technology Stack

| Layer | Technology | Role |
|---|---|---|
| Frontend | React, JavaScript, CSS | User interface and application interactions |
| Interactive maps | Leaflet / React Leaflet | Map rendering and geographic interaction |
| Geographic data | OpenStreetMap | Open geographic data and map context |
| Geographic queries | Overpass API | Query OpenStreetMap features matching store-related tags |
| Backend | Python, FastAPI | HTTP API and application logic |
| ASGI server | Uvicorn | Runs the FastAPI application |
| Deep learning | PyTorch, Torchvision | Model loading and image inference |
| Classifier | MobileNetV2 | Crop/disease image classification |
| Image processing | Pillow, NumPy | Image decoding and numerical preprocessing |
| Explainability | Grad-CAM tooling | Class-activation visualization |
| Persistence | SQLAlchemy with configured database | Diagnosis history and related records |
| PDF generation | ReportLab | Create PDF reports |
| Frontend hosting | Vercel | Publish the web application |
| Backend hosting | Render | Host the API service |
| Version control | Git, GitHub | Source management and collaboration |

Refer to `frontend/package.json` and `Backend/backend/requirements.txt` for the dependency versions and scripts in the checked-out version of the repository.

## 🏗️ System Architecture

```text
                         ┌────────────────────────┐
                         │      Web Browser       │
                         │      React UI          │
                         └───────────┬────────────┘
                                     │ HTTPS
                                     v
                         ┌────────────────────────┐
                         │    FastAPI Backend     │
                         │  CORS / API / Logic    │
                         └───────┬────────┬───────┘
                                 │        │
                  ┌──────────────┘        └────────────────┐
                  v                                         v
       ┌─────────────────────┐                  ┌─────────────────────┐
       │ Image/ML Pipeline   │                  │ Store Locator       │
       │ Validation          │                  │ Coordinate checks   │
       │ Preprocessing       │                  │ Overpass query      │
       │ MobileNetV2         │                  │ Distance calculation│
       │ Grad-CAM            │                  └──────────┬──────────┘
       └──────────┬──────────┘                             │
                  │                                        v
                  v                              ┌─────────────────────┐
       ┌─────────────────────┐                   │ OpenStreetMap data  │
       │ Treatment lookup    │                   │ / Overpass API      │
       │ History / PDF       │                   └─────────────────────┘
       └──────────┬──────────┘
                  │
                  v
       ┌─────────────────────┐
       │ Configured database │
       └─────────────────────┘
```

The frontend and backend are deployed separately. The frontend calls the backend over HTTPS. The backend loads the model and associated data, performs inference, and provides API responses to the frontend.

## 📁 Repository Structure

The main project areas are shown below. Use the current repository tree as the source of truth if a file has moved or been renamed.

```text
AgriScan/
├── frontend/                         # React frontend
│   ├── package.json                  # Frontend dependencies and scripts
│   └── ...                           # Pages, components, styling, API client, map UI
├── Backend/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI app and middleware/router setup
│   │   │   └── api/
│   │   │       ├── diagnose.py       # Diagnosis routes
│   │   │       ├── history.py        # Diagnosis history routes
│   │   │       └── stores.py         # Nearby agricultural-store route
│   │   ├── ml/
│   │   │   ├── src/
│   │   │   │   └── predict.py        # Model inference utilities
│   │   │   └── models/
│   │   │       └── mobilenetv2_test.pth
│   │   └── requirements.txt          # Python dependencies
│   └── data/
│       └── treatments.json           # Treatment lookup data (verify actual path)
└── README.md
```

Generated files, model outputs, database files, local virtual environments, and secrets should be handled according to the repository's ignore rules. Do not commit private credentials or user-uploaded images.

## 🌾 Crop Classes Supported

The model is designed for 38 crop/disease classes from the PlantVillage-style dataset family. Crop groups represented in this family include:

- Apple
- Blueberry
- Cherry
- Corn (maize)
- Grape
- Orange
- Peach
- Bell pepper
- Potato
- Raspberry
- Soybean
- Squash
- Strawberry
- Tomato

Labels include healthy categories and disease categories. Examples found in PlantVillage-style labels include apple scab, apple black rot, corn rust, grape black rot, potato early blight, potato late blight, and tomato leaf mold.

**The exact 38 labels and their order must be taken from the class-label mapping used by the model code.** The model output index must never be paired with a different label order. When replacing or retraining the model, update and test the mapping together with the checkpoint.

## 🧠 AI Model and Prediction Pipeline

### MobileNetV2

MobileNetV2 is a convolutional neural network designed to perform image recognition efficiently. AgriScan uses a trained MobileNetV2 checkpoint to classify leaf images into supported crop/disease categories.

### Inference stages

1. Decode the uploaded image.
2. Validate that the image can be opened and processed.
3. Convert it to the expected color format.
4. Resize and normalize it according to the model's preprocessing requirements.
5. Add the batch dimension required by PyTorch.
6. Run the model in inference mode.
7. Interpret the output scores and select the predicted class.
8. Associate the selected class with the correct label and confidence.
9. Generate Grad-CAM output where requested.
10. Retrieve treatment information and return the result to the frontend.

### Model artifact

The documented project layout includes a checkpoint under:

```text
Backend/backend/ml/models/mobilenetv2_test.pth
```

Confirm the actual model path in the current inference code before moving or replacing the file.

### Interpreting confidence

A confidence score describes how strongly the model favours a class relative to its alternatives. It is not necessarily a calibrated probability that the plant truly has that disease. Results can be affected by lighting, blur, background, leaf variety, multiple simultaneous conditions, and images outside the training distribution.

## 🔍 Grad-CAM Explainability

Grad-CAM (Gradient-weighted Class Activation Mapping) uses gradients associated with a selected class to create a coarse heatmap over an input image.

**Purpose**
- Show regions that contributed to the model's selected class score.
- Provide visual context alongside the predicted label.
- Help users inspect whether the model appears to focus on the leaf or on irrelevant background details.

**Important considerations**
- A heatmap is not a proof of correctness.
- The highlighted area is not a precise segmentation of a disease.
- Explanations can be misleading when the underlying prediction is wrong.
- Use the heatmap together with the image, confidence, and other available evidence.

## 🧴 Treatment Recommendation System

AgriScan associates model labels with treatment guidance using curated project data. The documented data file is `treatments.json`; check the current backend configuration for its exact path and expected schema.

### Lookup flow

1. The classifier returns a predicted class label.
2. The backend uses that label as the treatment lookup key.
3. Matching guidance is returned with the diagnosis when available.
4. The frontend displays the guidance as supporting information.

### Maintaining treatment data

- Keep keys consistent with the model's exact class labels.
- Validate the JSON format before deployment.
- Handle missing entries gracefully.
- Review content for accuracy and local relevance.
- Never imply that a treatment is guaranteed to work.
- Do not recommend pesticide use that conflicts with product labels or local regulations.

Treatment content is educational guidance and is not a substitute for advice from an agricultural extension service or qualified agronomist.

## 🗺️ Nearby Agricultural Store Locator

The store locator connects the map interface to geographic data so users can discover agricultural supply stores near a location. The feature combines browser location (when permitted), coordinate-based searches, backend API handling, OpenStreetMap/Overpass queries, distance calculations, and map presentation.

### Store-locator flow

1. The user opens the store-locator interface.
2. If the user chooses current location, the browser asks for permission.
3. The frontend obtains latitude and longitude, or uses coordinates selected/provided by the user.
4. The frontend sends a request to the AgriScan backend.
5. The backend validates the coordinates and radius.
6. The backend constructs and sends a geographic query to the configured Overpass API.
7. The response is parsed and mapped to the application's store-result structure.
8. The backend calculates straight-line distances where supported.
9. The frontend displays results on the interactive map and in its associated list.
10. The user can inspect a store and use available map/directions links.

### Map technology

**Leaflet / React Leaflet**
- Renders the interactive map.
- Supports panning, zooming, markers, and popups.
- Connects map interactions to React application state.

**OpenStreetMap**
- Supplies open geographic data and, where configured, map tiles.
- Requires appropriate attribution when its data or tiles are displayed.

**Overpass API**
- Provides query access to OpenStreetMap data.
- Can be used to find mapped features matching tags and a geographic search area.
- Is a public service with finite resources; request limits, timeouts, and temporary unavailability must be handled.

**Haversine distance**
- Computes approximate straight-line distance between geographic coordinates.
- Does not represent road distance, driving time, or a guarantee that a route is accessible.

### Nearby-store endpoint

The application uses the following endpoint pattern:

```http
GET /api/stores/nearby?lat=<latitude>&lng=<longitude>&radius=<radius_in_meters>
```

Example:

```text
https://agriscan-6up4.onrender.com/api/stores/nearby?lat=16.30&lng=80.44&radius=5000
```

The coordinates are illustrative only. The observed `radius=5000` represents a 5,000-metre (5 km) search radius. The exact allowed radius options should match the frontend and backend validation.

### Input validation

The backend should validate:
- Latitude is between `-90` and `90`.
- Longitude is between `-180` and `180`.
- Radius is positive and within an acceptable maximum.
- Query parameters are present and numeric.
- The upstream response has the expected structure.

### Empty results and errors

The map should distinguish between:
- **Stores found:** render results and markers.
- **No stores found:** show an informative empty state.
- **Location denied/unavailable:** explain how to enable location or provide coordinates manually.
- **Invalid coordinates/radius:** return a clear validation error.
- **Upstream timeout or outage:** show a temporary service error and allow a later retry.
- **Map tiles unavailable:** preserve useful result information if possible, and distinguish tile rendering from store-search failures.

A failed upstream query should never be replaced with fabricated store listings.

### Reliability recommendations

For a robust deployment:
- Keep external Overpass calls in the backend.
- Make the Overpass endpoint configurable.
- Use explicit connection and read timeouts.
- Handle HTTP status errors, invalid JSON, and unexpected payloads.
- Use only a small bounded retry policy for transient errors.
- Cache successful searches briefly where appropriate.
- Avoid overly broad geographic queries and excessive request frequency.
- Respect the usage policies of the chosen Overpass instance and map-tile provider.
- Include OpenStreetMap attribution in the map UI.
- Keep the response schema consistent between backend and frontend.

### Map troubleshooting

If the map does not show stores:
1. Check `GET /health` to confirm the backend responds.
2. Open `/docs` and verify the nearby-store route and its query parameters.
3. Try a valid latitude, longitude, and radius.
4. Inspect the backend logs for the store request and underlying exception.
5. Check whether the configured Overpass endpoint is responding.
6. Validate the Overpass query and returned JSON independently.
7. Confirm that the frontend parameter names match the backend route.
8. Inspect the browser Network panel to distinguish API failures from tile-loading errors.
9. Test location permission denial, empty results, invalid coordinates, and upstream timeouts.
10. Confirm the frontend and backend production URLs and CORS configuration.

### Mapping attribution and service policies

When displaying OpenStreetMap data or tiles, provide the attribution required by the relevant provider. Public Overpass instances do not provide a guaranteed production service level. Check the policies of the specific endpoint and tile provider configured for the application before scaling traffic.

## 🗂️ Diagnosis History

The backend includes a history API module and a SQLAlchemy persistence layer. The history workflow is intended to let users revisit previous diagnoses.

Typical information that a diagnosis record may contain includes a predicted class, confidence, timestamps, and references to generated artifacts, depending on the current database model.

To maintain this feature:
- Confirm the active database URL and schema.
- Apply database migrations or initialization steps required by the current code.
- Validate that a record is saved only after an appropriate diagnosis operation.
- Handle database errors without crashing unrelated API routes.
- Avoid storing unnecessary personal information or original images without a clear need and appropriate consent.
- Test history retrieval after backend restarts to confirm the selected database provides the expected persistence.

The exact record schema and history route names are defined by the current backend source and FastAPI OpenAPI documentation.

## 📄 PDF Diagnosis Reports

AgriScan uses ReportLab for PDF generation. The report workflow is intended to make diagnosis information available in a portable format.

Depending on the current report implementation, a report may include:
- Predicted crop/disease label
- Confidence information
- Diagnosis timestamp
- Treatment guidance
- Grad-CAM or result-image references where configured

The exact fields depend on the report endpoint and current implementation. Validate PDF generation with a successful diagnosis and ensure temporary files are handled safely.

## 🔌 Backend API

The FastAPI backend provides endpoints for health checks, diagnosis, store lookup, history, and report-related operations.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health/status check |
| `POST` | `/api/predict` | Submit an image for prediction |
| `GET` | `/api/stores/nearby` | Search for nearby agricultural stores |
| Various | History endpoints | Save/retrieve diagnosis history as implemented |
| Various | Report endpoints | Generate or retrieve PDF reports as implemented |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/openapi.json` | OpenAPI schema |

History and report methods and exact paths can vary. The live OpenAPI schema is the authoritative reference.

### Example: health check

```bash
curl https://agriscan-6up4.onrender.com/health
```

### Example: diagnosis upload

The multipart field name must match the one declared by the current route. A typical example is:

```bash
curl -X POST "https://agriscan-6up4.onrender.com/api/predict" \
  -H "accept: application/json" \
  -F "file=@leaf.jpg"
```

If the route uses a different field name, use the name shown at `/docs`.

### Example: nearby-store lookup

```bash
curl "https://agriscan-6up4.onrender.com/api/stores/nearby?lat=16.30&lng=80.44&radius=5000"
```

Replace the example coordinates with valid coordinates for the desired search area.

## 💻 Installation and Local Development

### Prerequisites

- Git
- Python compatible with `Backend/backend/requirements.txt` (the deployment has used Python 3.11)
- Node.js and npm compatible with `frontend/package.json`
- The model checkpoint and treatment data expected by the backend
- Database configuration if using persistent history

### 1. Clone the repository

```bash
git clone https://github.com/aditya2806406/AgriScan.git
cd AgriScan
```

To work on the verification branch:

```bash
git checkout agriscan-memory-verification
```

### 2. Create and activate the backend environment

```bash
cd Backend/backend
python -m venv .venv
```

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**
```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use the dependency versions in the checked-out branch. PyTorch and Torchvision versions should be compatible with each other and with the target CPU/GPU environment.

### 4. Start the backend

Run from `Backend/backend`, where the `app` package is available:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful URLs:
- Health: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

### 5. Install and start the frontend

Open another terminal at the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by the development server. Check `frontend/package.json` for the actual scripts supported by the current frontend.

### 6. Configure the frontend API URL

Set the frontend's API base URL to the local backend origin (`http://127.0.0.1:8000`) using the exact environment-variable name read by the current frontend. Restart the frontend after changing configuration.

### 7. Verify the setup

- Confirm the backend health route responds.
- Open Swagger UI and inspect the available routes.
- Submit a valid leaf image.
- Confirm the model checkpoint and treatment data load.
- Check Grad-CAM output generation.
- Test history and report operations if their dependencies are configured.
- Test the store locator with valid coordinates and inspect both browser and backend logs.

## ⚙️ Environment Configuration

Environment-variable names must match the actual names read in the current code. Review `Backend/backend/app/main.py`, the database configuration, model-loading code, and frontend API client before adding variables.

| Setting | Purpose | Notes |
|---|---|---|
| `PORT` | Port provided by Render | Start Uvicorn using the platform's port |
| `ALLOW_MOCK` | Mock/fallback prediction behavior if referenced by the application | Verify its exact semantics in the source; use real inference for production diagnosis |
| Database URL | SQLAlchemy database connection | Use the variable name expected by the database module |
| Frontend API base URL | Backend origin used by the frontend | Use the frontend's actual variable name |
| Overpass endpoint | Geographic query service if configurable | Prefer server-side configuration |
| Model path | Location of the model checkpoint if configurable | Must point to the correct checkpoint |
| Treatment data path | Location of treatment lookup data | Must point to the expected JSON file |

### Secrets and configuration best practices

- Keep `.env` files out of Git.
- Never place private API keys or database credentials in frontend variables.
- Configure production variables in the hosting provider's environment settings.
- Restrict CORS to the required frontend origins.
- Do not log credentials, tokens, or sensitive image data.
- Restart or redeploy the service after changing production environment variables.

## 🚀 Deployment

### Frontend — Vercel

Live frontend: https://agri-scan-olive.vercel.app/

Typical deployment steps:
1. Import the GitHub repository into Vercel.
2. Set the frontend project/root directory to the directory containing its `package.json`.
3. Configure the production backend API base URL using the frontend's expected variable name.
4. Install dependencies and use the build command declared by the frontend project.
5. Deploy and test the live URL.
6. Check the browser console and Network panel if API requests fail.

### Backend — Render

Live backend: https://agriscan-6up4.onrender.com

The deployment has used the following configuration:
- **Root directory:** `Backend/backend`
- **Runtime:** Python
- **Python version:** 3.11
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Confirm these values against the service's current settings and repository layout before redeploying.

Deployment checklist:
1. Select the intended Git branch.
2. Confirm the root directory and requirements file.
3. Configure environment variables in Render.
4. Confirm model and treatment data are available at runtime.
5. Check build logs and startup logs.
6. Verify `/health` and `/docs`.
7. Test diagnosis, history, report generation, and store lookup independently.
8. Verify that CORS allows the deployed frontend origin.

### CORS

The backend should permit the deployed frontend origin and any required local development origin. Use the exact production URL, avoid unnecessary wildcard origins when credentials are involved, and ensure the CORS settings match the authentication model.

## 🧪 Testing

Test the features independently so that a failure in one external dependency does not hide whether the rest of the application works.

### Diagnosis tests
- Valid leaf image.
- Unsupported or malformed image.
- Empty upload.
- Corrupted image.
- Very large image.
- Low-confidence prediction.
- Image that is not a crop leaf.
- Repeated request after an invalid image to ensure the backend remains responsive.

### Store locator tests
- Valid coordinates and normal radius.
- Invalid latitude or longitude.
- Missing or non-numeric query parameters.
- Empty search results.
- Upstream timeout.
- Upstream HTTP error or invalid JSON.
- Location permission denied.
- Map tile loading failure.
- Repeated requests and caching behavior.

### History and report tests
- Save and retrieve a diagnosis.
- Verify persistence after backend restart.
- Handle an empty history.
- Generate a report for a valid diagnosis.
- Handle missing images or report data gracefully.

### Deployment tests
- Health endpoint returns the expected status.
- Frontend can call the deployed API.
- CORS permits the intended origin.
- Model and treatment data load successfully.
- Logs contain no exposed credentials.
- External-service failures produce clear, controlled errors.

## 🛠️ Troubleshooting

| Problem | Possible cause | What to check |
|---|---|---|
| Backend fails to start | Dependency mismatch, wrong working directory, missing model/data | Build logs, requirements, start command, file paths |
| Model fails to load | Incorrect checkpoint path or incompatible versions | Model path and PyTorch/Torchvision compatibility |
| Prediction request fails | Incorrect multipart field, unreadable image, backend exception | `/docs`, request payload, Render logs |
| Frontend cannot reach API | Incorrect API base URL or CORS | Browser Network panel and backend CORS configuration |
| Grad-CAM image missing | Model-layer configuration or output-file path | Inference logs and output directory |
| Treatment guidance missing | Predicted label does not match a treatment key | Class-label mapping and treatment JSON |
| History is not persistent | Database configuration or storage lifecycle | Database URL, schema, and backend logs |
| PDF generation fails | Missing report data or file permissions | Report endpoint logs and ReportLab dependencies |
| Store search fails | Overpass timeout, bad query, parsing issue, or configuration | Store-route logs and upstream response |
| Map appears blank | Tile URL/network issue or map container sizing | Browser console, tile requests, and CSS container height |
| No stores appear | No mapped features in area, wrong tags, or empty query response | Query, coordinates, radius, and response structure |
| Browser location fails | Permission denied, insecure context, or unavailable location | Browser permissions and HTTPS configuration |
| Render service starts slowly | Model loading or cold start | Startup logs and health-check configuration |

## 🔐 Security, Privacy and Responsible Use

- Validate file type and image content on the server; do not trust file extensions alone.
- Limit upload size and handle malformed or decompression-heavy images safely.
- Avoid returning internal exception traces to users.
- Keep credentials and database URLs in server-side environment variables.
- Configure CORS deliberately.
- Avoid collecting more location or personal data than necessary.
- Ask for browser location permission through the standard browser API; provide a fallback when location is denied.
- Do not fabricate store results if geographic data is unavailable.
- Respect OpenStreetMap attribution and the policies of the configured Overpass and tile providers.
- Treat predictions and treatment guidance as informational, not as a guaranteed diagnosis or cure.

## ⚠️ Limitations

- The classifier is limited to the labels and visual patterns represented in its training data.
- Real-world photos can differ substantially from curated training images.
- Model confidence does not guarantee correctness.
- Grad-CAM is an approximate visual explanation.
- Treatment guidance depends on the quality and coverage of the curated lookup data.
- Store locator results depend on the completeness and freshness of OpenStreetMap data.
- Public Overpass and map-tile services may impose usage limits or experience outages.
- Straight-line distance is not the same as road distance or travel time.
- Persistent history depends on the configured database and deployment storage.
- AgriScan does not replace professional agronomic assessment.

## 🧭 Future Enhancements

- Expand and validate training data from varied real-world growing conditions.
- Evaluate model accuracy and calibration on an independent test set.
- Add more crops and disease categories.
- Improve multilingual treatment guidance.
- Add offline-friendly result access where feasible.
- Improve map filtering, radius selection, store categories, and directions.
- Add robust caching and graceful degradation for geographic service outages.
- Add automated integration tests for diagnosis, history, reports, and mapping.
- Improve accessibility and mobile responsiveness.
- Add monitoring for API latency and external service failures.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a focused feature branch.
3. Make a small, well-scoped change.
4. Run relevant tests and check formatting.
5. Verify that no secrets or personal data are included.
6. Open a pull request with a clear summary and test results.

For changes involving model labels, update the checkpoint and class mapping consistently. For map changes, test both successful store results and upstream failure scenarios.

## 📜 License

Add the project's chosen license to the repository before distributing or reusing the code. Unless a license file is present, do not assume that the repository grants broad permission to reuse or redistribute its contents.
