# ShadeRoute AI — Smart Shadow Navigation System
**Bengaluru · 12.9716°N · 77.5946°E**

## Quick Start (3 commands)

```bash
conda activate shaderoute
cd path/to/shaderoute-project/backend
python run.py
```

Then open: http://localhost:8000/ui

---

## Full Setup Guide

### Step 1 — Create Conda Environment
```bash
conda create -n shaderoute python=3.11
conda activate shaderoute
```

### Step 2 — Install Packages
```bash
cd backend
pip install fastapi uvicorn[standard] pysolar pytz python-multipart
```

### Step 3 — Start Backend
```bash
python run.py
```

### Step 4 — Open Frontend
**Option A (via backend):**  http://localhost:8000/ui

**Option B (direct):** Double-click frontend/index.html

**Option C (Python server):**
```bash
cd frontend
python -m http.server 3000
# Open: http://localhost:3000
```

---

## Project Structure
```
shaderoute-project/
├── backend/
│   ├── main.py          ← FastAPI app (all API routes)
│   ├── run.py           ← Start script
│   └── requirements.txt ← Dependencies
├── frontend/
│   └── index.html       ← Full UI (connected to backend)
└── README.md
```

## API Endpoints
| Endpoint | Description |
|---|---|
| GET /api/health | Health check |
| GET /api/sun | Real-time sun position |
| GET /api/environment | Temp, AQI, humidity, UV |
| POST /api/route | Compute shaded route |
| GET /api/routes/compare | Compare cool/fast/safe |
| GET /api/heat | Heat zone status |
| GET /api/heat/forecast | 24hr forecast |
| GET /api/shadow | Shadow map data |
| GET /api/sensors | IoT sensor readings |
| GET /api/suggestions | AI route suggestions |
| POST /api/heat-stress | WBGT calculator |
| GET /api/dashboard | All dashboard data |
| GET /api/landmarks | Bengaluru landmarks |
| GET /api/profile | User profile |

## Bengaluru Landmarks Covered
- Lalbagh Garden (12.9508°N, 77.5848°E) — 88% shade
- Cubbon Park (12.9763°N, 77.5929°E) — 85% shade
- MG Road (12.9747°N, 77.6069°E) — 72% shade
- Silk Board (12.9176°N, 77.6228°E) — HEAT ZONE
- Indiranagar 100ft (12.9784°N, 77.6408°E)
- Koramangala 5th Block (12.9344°N, 77.6249°E)
- Ulsoor Lake (12.9830°N, 77.6207°E) — 70% shade
- Malleswaram (13.0023°N, 77.5689°E) — 65% shade
