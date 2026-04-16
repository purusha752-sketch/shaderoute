"""
ShadeRoute AI — Backend API
Smart Shadow-Based Navigation System — Bengaluru
Connects with ShadeRoute_UI.html frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import math, random, datetime, os
import pytz

try:
    from pysolar.solar import get_altitude, get_azimuth
    PYSOLAR = True
except ImportError:
    PYSOLAR = False

# ─── APP ───────────────────────────────────────
app = FastAPI(
    title="ShadeRoute AI",
    description="Smart Shadow-Based Navigation — Bengaluru",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

# ─── MODELS ────────────────────────────────────
class RouteRequest(BaseModel):
    origin_lat:   float = 12.9344
    origin_lon:   float = 77.6249
    dest_lat:     float = 12.9747
    dest_lon:     float = 77.6069
    mode:         str   = "cool"
    user_age:     int   = 30

class HeatStressRequest(BaseModel):
    age:           int   = 30
    temperature_c: float = 38.0
    humidity_pct:  float = 65.0
    shadow_pct:    float = 50.0
    distance_km:   float = 2.0
    speed_kmh:     float = 5.0

# ─── BENGALURU DATA ────────────────────────────
HEAT_ZONES = [
    {"id":"HZ-001","name":"Silk Board Junction",    "lat":12.9176,"lon":77.6228,"level":"EXTREME","temp_c":44.8},
    {"id":"HZ-002","name":"Marathahalli Bridge",    "lat":12.9558,"lon":77.7012,"level":"HIGH",   "temp_c":43.2},
    {"id":"HZ-003","name":"Majestic Bus Stand",     "lat":12.9777,"lon":77.5727,"level":"HIGH",   "temp_c":42.7},
    {"id":"HZ-004","name":"Electronic City Phase1", "lat":12.8452,"lon":77.6602,"level":"HIGH",   "temp_c":43.6},
    {"id":"HZ-005","name":"Whitefield Main Road",   "lat":12.9698,"lon":77.7499,"level":"MODERATE","temp_c":41.4},
    {"id":"HZ-006","name":"Outer Ring Road",        "lat":12.9559,"lon":77.6962,"level":"MODERATE","temp_c":41.8},
    {"id":"HZ-007","name":"Bannerghatta Road",      "lat":12.9000,"lon":77.5950,"level":"MODERATE","temp_c":40.9},
    {"id":"HZ-008","name":"Rajajinagar Industrial", "lat":12.9909,"lon":77.5512,"level":"MODERATE","temp_c":41.2},
]

SHADE_ZONES = [
    {"id":"SZ-001","name":"Lalbagh Garden",    "lat":12.9508,"lon":77.5848,"shade_pct":88,"ndvi":0.68},
    {"id":"SZ-002","name":"Cubbon Park",       "lat":12.9763,"lon":77.5929,"shade_pct":85,"ndvi":0.65},
    {"id":"SZ-003","name":"MG Road Avenue",    "lat":12.9747,"lon":77.6069,"shade_pct":72,"ndvi":0.44},
    {"id":"SZ-004","name":"Church Street",     "lat":12.9763,"lon":77.6070,"shade_pct":68,"ndvi":0.44},
    {"id":"SZ-005","name":"Malleswaram Cross", "lat":13.0023,"lon":77.5689,"shade_pct":65,"ndvi":0.52},
    {"id":"SZ-006","name":"Ulsoor Lake Walk",  "lat":12.9830,"lon":77.6207,"shade_pct":70,"ndvi":0.55},
    {"id":"SZ-007","name":"Jayanagar 4th Blk", "lat":12.9258,"lon":77.5826,"shade_pct":60,"ndvi":0.48},
    {"id":"SZ-008","name":"Sankey Tank",       "lat":13.0070,"lon":77.5811,"shade_pct":74,"ndvi":0.58},
]

LANDMARKS = [
    {"key":"lalbagh",    "name":"Lalbagh Garden",      "lat":12.9508,"lon":77.5848,"shade":88,"temp":34.2,"ndvi":0.68,"type":"COOL"},
    {"key":"cubbon",     "name":"Cubbon Park",          "lat":12.9763,"lon":77.5929,"shade":85,"temp":34.8,"ndvi":0.65,"type":"COOL"},
    {"key":"mgroad",     "name":"MG Road",              "lat":12.9747,"lon":77.6069,"shade":72,"temp":38.4,"ndvi":0.32,"type":"MODERATE"},
    {"key":"silkboard",  "name":"Silk Board Junction",  "lat":12.9176,"lon":77.6228,"shade":8, "temp":44.8,"ndvi":0.08,"type":"EXTREME"},
    {"key":"indiranagar","name":"Indiranagar 100ft Rd", "lat":12.9784,"lon":77.6408,"shade":55,"temp":37.8,"ndvi":0.42,"type":"MODERATE"},
    {"key":"koramangala","name":"Koramangala 5th Block","lat":12.9344,"lon":77.6249,"shade":50,"temp":38.2,"ndvi":0.38,"type":"MODERATE"},
    {"key":"ulsoor",     "name":"Ulsoor Lake",          "lat":12.9830,"lon":77.6207,"shade":70,"temp":35.6,"ndvi":0.55,"type":"COOL"},
    {"key":"malleswaram","name":"Malleswaram 8th Cross","lat":13.0023,"lon":77.5689,"shade":65,"temp":36.4,"ndvi":0.52,"type":"GOOD"},
]

# ─── HELPERS ───────────────────────────────────
def get_sun(lat: float = 12.9716, lon: float = 77.5946) -> dict:
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    if PYSOLAR:
        alt = get_altitude(lat, lon, now)
        azi = get_azimuth(lat, lon, now)
    else:
        h   = now.hour + now.minute / 60
        alt = max(0, 60 * math.sin(math.pi * (h - 6) / 12))
        azi = 90 + (h - 6) * 15
    shd = round(1 / max(math.tan(math.radians(max(alt, 1))), 0.01), 2)
    uv  = round(max(0, 0.21 * math.sin(math.radians(max(alt, 0))) * 12), 1)
    return {
        "altitude_deg":     round(alt, 2),
        "azimuth_deg":      round(azi, 2),
        "shadow_length_x":  shd,
        "shadow_direction": round((azi + 180) % 360, 1),
        "uv_index":         uv,
        "timestamp":        now.isoformat(),
        "best_walking":     bool(alt < 25.0),
    }

def haversine(la1, lo1, la2, lo2) -> float:
    R  = 6371
    d1 = (la2 - la1) * math.pi / 180
    d2 = (lo2 - lo1) * math.pi / 180
    a  = (math.sin(d1/2)**2
          + math.cos(la1*math.pi/180) * math.cos(la2*math.pi/180) * math.sin(d2/2)**2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 3)

def make_waypoints(la1, lo1, la2, lo2, n=6):
    pts = []
    for i in range(n):
        t   = i / (n - 1)
        lat = la1 + (la2 - la1)*t + (random.random() - .5)*0.001
        lon = lo1 + (lo2 - lo1)*t + (random.random() - .5)*0.001
        pts.append({"lat":round(lat,6),"lon":round(lon,6),
                    "shadow_pct":random.randint(40,90),
                    "temp_c":round(random.uniform(34,42),1)})
    return pts

def wbgt_calc(temp, hum, shadow, age):
    return round(0.7*(temp*hum/100) + 0.2*(temp*(100-shadow)/100)
                 + 0.1*temp + max(0,(age-40)*0.1), 1)

# ─── SYSTEM ────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "system":  "ShadeRoute AI — Smart Shadow Navigation",
        "version": "1.0.0",
        "status":  "ONLINE",
        "city":    "Bengaluru, Karnataka, India  12.9716N 77.5946E",
        "frontend":"/",
        "docs":    "/docs",
        "pysolar": PYSOLAR,
    }

@app.get("/api/health", tags=["System"])
async def health():
    return {"status":"healthy","pysolar":PYSOLAR,
            "time":datetime.datetime.now().isoformat()}

# ─── SUN ───────────────────────────────────────
@app.get("/api/sun", tags=["Sun"])
async def sun_now(lat: float = 12.9716, lon: float = 77.5946):
    return get_sun(lat, lon)

@app.get("/api/sun/hourly", tags=["Sun"])
async def sun_hourly():
    hours = []
    for h in range(6, 20):
        alt  = max(0, 60*math.sin(math.pi*(h-6)/12))
        azi  = 90 + (h-6)*15
        hours.append({
            "hour":    h,
            "label":   f"{h:02d}:00",
            "altitude":round(alt, 1),
            "azimuth": round(azi, 1),
            "shadow_x":round(1/max(math.tan(math.radians(max(alt,1))),0.01), 2),
            "uv_index":round(max(0, 0.21*math.sin(math.radians(max(alt,0)))*12), 1),
            "walkable":bool(alt < 30),
        })
    return {"city":"Bengaluru","hours":hours}

# ─── ROUTING ───────────────────────────────────
@app.post("/api/route", tags=["Routing"])
async def compute_route(req: RouteRequest):
    sun  = get_sun(req.origin_lat, req.origin_lon)
    dist = haversine(req.origin_lat, req.origin_lon, req.dest_lat, req.dest_lon)
    eta  = round((dist / 5) * 60)

    cfg = {
        "cool": {"shadow":0.75,"heat":0.25,"tree":0.70,"crowd":0.3},
        "fast": {"shadow":0.32,"heat":0.50,"tree":0.35,"crowd":0.4},
        "safe": {"shadow":0.55,"heat":0.35,"tree":0.50,"crowd":0.2},
    }.get(req.mode, {"shadow":0.75,"heat":0.25,"tree":0.70,"crowd":0.3})

    score = round(max(0, min(1,
        0.28*cfg["shadow"] + 0.15*cfg["tree"] - 0.22*cfg["heat"] - 0.08*cfg["crowd"]
    )), 3)

    shadow_pct = round(cfg["shadow"] * 100)
    temp_c     = round(35 + cfg["heat"] * 8, 1)
    wbgt       = wbgt_calc(temp_c, 65, shadow_pct, req.user_age)
    risk       = ("LOW" if wbgt < 28 else "MODERATE" if wbgt < 32
                  else "HIGH" if wbgt < 35 else "EXTREME")

    return {
        "route_id":        f"RT-{random.randint(1000,9999)}",
        "mode":            req.mode,
        "city":            "Bengaluru",
        "origin":          {"lat":req.origin_lat,"lon":req.origin_lon},
        "destination":     {"lat":req.dest_lat,  "lon":req.dest_lon},
        "distance_km":     dist,
        "duration_min":    eta,
        "route_score":     score,
        "shadow_pct":      shadow_pct,
        "tree_cover_pct":  round(cfg["tree"] * 100),
        "avg_temp_c":      temp_c,
        "heat_stress": {
            "wbgt_c":    wbgt,
            "risk_level":risk,
            "risk_pct":  round(wbgt/40*100),
            "advice": {
                "LOW":      "Safe — carry water, wear hat",
                "MODERATE": "Hydrate every 15 min",
                "HIGH":     "Seek shade, rest often",
                "EXTREME":  "AVOID walking — find shelter"
            }[risk],
            "water_ml":  int(dist * 250 * (1 + (temp_c - 30) * 0.05)),
        },
        "sun":       sun,
        "waypoints": make_waypoints(req.origin_lat, req.origin_lon,
                                    req.dest_lat,   req.dest_lon),
        "alternatives": [
            {"mode":"balanced","distance_km":round(dist*.9,1),
             "shadow_pct":round(shadow_pct*.9),"score":round(score*.92,2)},
            {"mode":"shortest","distance_km":round(dist*.75,1),
             "shadow_pct":round(shadow_pct*.6),"score":round(score*.76,2)},
        ],
    }

@app.get("/api/routes/compare", tags=["Routing"])
async def compare_routes(
    origin_lat:float=12.9344, origin_lon:float=77.6249,
    dest_lat:  float=12.9747, dest_lon:  float=77.6069
):
    dist = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    return {
        "city":"Bengaluru","base_km":dist,
        "routes":{
            "cool":{"distance_km":round(dist*1.15,1),"duration_min":round(dist*1.15/5*60),
                    "shadow_pct":72,"avg_temp_c":36.2,"score":0.84,
                    "description":"Via Church St & MG Road tree avenue — most shaded"},
            "fast":{"distance_km":round(dist*.92,1),"duration_min":round(dist*.92/5*60),
                    "shadow_pct":31,"avg_temp_c":41.0,"score":0.68,
                    "description":"Direct path — shorter but sun exposed"},
            "safe":{"distance_km":round(dist*1.22,1),"duration_min":round(dist*1.22/5*60),
                    "shadow_pct":58,"avg_temp_c":37.5,"score":0.79,
                    "description":"Residential streets — low crime, low crowd"},
        }
    }

# ─── HEAT ──────────────────────────────────────
@app.get("/api/heat", tags=["Heat"])
async def heat_status():
    return {
        "city":"Bengaluru",
        "avg_temp_c":   round(random.uniform(37,40),1),
        "peak_temp_c":  round(random.uniform(42,46),1),
        "peak_location":"Silk Board Junction  12.9176N 77.6228E",
        "humidity_pct": random.randint(55,72),
        "feels_like_c": round(random.uniform(39,44),1),
        "uhi_intensity":"HIGH",
        "hot_zones":    8,
        "zones":        HEAT_ZONES,
    }

@app.get("/api/heat/forecast", tags=["Heat"])
async def heat_forecast():
    return {"city":"Bengaluru","forecast":[
        {"hour":h,"label":f"{h:02d}:00",
         "temp_c":max(28,round(32+10*math.sin(math.pi*(h-6)/12)+random.uniform(-1,1),1)),
         "shadow_pct":round(max(0,80*math.sin(math.pi*h/24)),1)}
        for h in range(24)
    ]}

# ─── SHADOW ────────────────────────────────────
@app.get("/api/shadow", tags=["Shadow"])
async def shadow_map():
    return {
        "city":"Bengaluru","sun":get_sun(),
        "avg_coverage_pct":43,
        "zones":SHADE_ZONES,
        "updated_at":datetime.datetime.now().isoformat(),
    }

# ─── ENVIRONMENT ───────────────────────────────
@app.get("/api/environment", tags=["Environment"])
async def environment():
    sun = get_sun()
    return {
        "city":          "Bengaluru",
        "coords":        {"lat":12.9716,"lon":77.5946},
        "sun":           sun,
        "temperature_c": round(random.uniform(36,41), 1),
        "feels_like_c":  round(random.uniform(39,44), 1),
        "humidity_pct":  random.randint(55,72),
        "aqi":           random.randint(110,165),
        "pm25":          round(random.uniform(45,120), 1),
        "uv_index":      sun["uv_index"],
        "wind_kmh":      random.randint(5,18),
        "wind_dir":      "SW",
        "cloud_pct":     random.randint(5,35),
        "shadow_avg_pct":43,
        "tree_cover_pct":38,
        "ndvi_avg":      0.42,
        "hot_zones":     8,
        "conditions":    "Partly Sunny · Hot",
        "walking_advice":"Best: 6-9 AM or after 5 PM",
        "updated_at":    datetime.datetime.now().isoformat(),
    }

# ─── SENSORS ───────────────────────────────────
@app.get("/api/sensors", tags=["IoT"])
async def sensors():
    data = [
        {"id":"BLRS-001","type":"temperature","lat":12.9747,"lon":77.6069,"location":"MG Road",
         "value":round(random.uniform(36,42),1),"unit":"°C"},
        {"id":"BLRS-002","type":"aqi",        "lat":12.9176,"lon":77.6228,"location":"Silk Board",
         "value":random.randint(150,200),"unit":"AQI"},
        {"id":"BLRS-003","type":"temperature","lat":12.9344,"lon":77.6249,"location":"Koramangala",
         "value":round(random.uniform(35,41),1),"unit":"°C"},
        {"id":"BLRS-004","type":"crowd",      "lat":12.9777,"lon":77.5727,"location":"Majestic",
         "value":round(random.uniform(0.5,0.9),2),"unit":"density"},
        {"id":"BLRS-005","type":"aqi",        "lat":12.9558,"lon":77.7012,"location":"Marathahalli",
         "value":random.randint(140,190),"unit":"AQI"},
        {"id":"BLRS-006","type":"temperature","lat":12.9784,"lon":77.6408,"location":"Indiranagar",
         "value":round(random.uniform(35,40),1),"unit":"°C"},
        {"id":"BLRS-007","type":"uv",         "lat":12.9508,"lon":77.5848,"location":"Lalbagh",
         "value":round(get_sun()["uv_index"],1),"unit":"UV Index"},
        {"id":"BLRS-008","type":"temperature","lat":12.9698,"lon":77.7499,"location":"Whitefield",
         "value":round(random.uniform(37,43),1),"unit":"°C"},
    ]
    return {"city":"Bengaluru","count":len(data),"sensors":data,
            "updated_at":datetime.datetime.now().isoformat()}

# ─── AI SUGGESTIONS ────────────────────────────
@app.get("/api/suggestions", tags=["AI"])
async def ai_suggestions():
    sun = get_sun()
    h   = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).hour
    return {
        "city":"Bengaluru","sun":sun,
        "wbgt_c": wbgt_calc(38, 65, 50, 30),
        "risk":   "LOW",
        "suggestions":[
            {"id":"SUG-001","icon":"🌿","title":"This route is cooler by 3°C",
             "detail":"Via Church Street — 68% shaded · Rain tree canopy",
             "tag":"Cool Route","tag_color":"green","impact":"−3°C","priority":"HIGH"},
            {"id":"SUG-002","icon":"🌳","title":"More trees available ahead",
             "detail":"Lalbagh Boulevard — 800m Rain tree canopy",
             "tag":"NDVI 0.68","tag_color":"sky","impact":"88% shade","priority":"HIGH"},
            {"id":"SUG-003","icon":"💨","title":"Less pollution via this path",
             "detail":"Avoid Silk Board AQI 188 · Lane AQI 92",
             "tag":"Air Quality","tag_color":"sky","impact":"AQI −96","priority":"MEDIUM"},
            {"id":"SUG-004","icon":"☀️",
             "title":"Best walking window: 6–9 AM" if h<9 else "Avoid 11AM–3PM now",
             "detail":f"Sun alt {sun['altitude_deg']}° · Shadow {sun['shadow_length_x']}x · UV {sun['uv_index']}",
             "tag":"Sun Alert" if 10<h<16 else "Good Window",
             "tag_color":"amber" if 10<h<16 else "green",
             "impact":"High" if h<9 or h>17 else "Moderate","priority":"MEDIUM"},
        ],
        "urban_tips":[
            {"location":"Silk Board","lat":12.9176,"lon":77.6228,
             "action":"Plant 20 Rain Trees","impact":"−4.5°C LST","cost":"₹4.2 lakh"},
            {"location":"Marathahalli","lat":12.9558,"lon":77.7012,
             "action":"Install shade canopy","impact":"−3.8°C felt","cost":"₹8.5 lakh"},
        ],
    }

# ─── HEAT STRESS ───────────────────────────────
@app.post("/api/heat-stress", tags=["Health"])
async def heat_stress_calc(req: HeatStressRequest):
    wbgt = wbgt_calc(req.temperature_c, req.humidity_pct, req.shadow_pct, req.age)
    risk = ("LOW" if wbgt<28 else "MODERATE" if wbgt<32
            else "HIGH" if wbgt<35 else "EXTREME")
    return {
        "wbgt_c":    wbgt,
        "risk_level":risk,
        "risk_pct":  round(wbgt/40*100),
        "advice": {
            "LOW":      "Safe — carry water",
            "MODERATE": "Hydrate every 15 min, wear hat",
            "HIGH":     "Rest every 10 min, seek shade",
            "EXTREME":  "AVOID walking — find shelter",
        }[risk],
        "water_ml": int(req.distance_km*250*(1+(req.temperature_c-30)*0.05)),
    }

# ─── DASHBOARD ─────────────────────────────────
@app.get("/api/dashboard", tags=["Dashboard"])
async def dashboard():
    sun = get_sun()
    hourly = [
        {"hour":h,"label":f"{h:02d}:00",
         "temp_c":max(28,round(30+12*math.sin(math.pi*(h-6)/12)+random.uniform(-1,1),1)),
         "shadow_pct":round(max(0,80*math.sin(math.pi*h/24)),1)}
        for h in range(6,22)
    ]
    return {
        "city":"Bengaluru","coords":{"lat":12.9716,"lon":77.5946},
        "sun":sun,
        "peak_heat_c":44.8,"peak_heat_location":"Silk Board Junction",
        "avg_shadow_pct":43,"avg_ndvi":0.42,"active_heat_zones":8,
        "hourly_temp":hourly,
        "zone_shadows":[
            {"zone":"Lalbagh Garden","shadow_pct":88},{"zone":"Cubbon Park","shadow_pct":85},
            {"zone":"MG Road","shadow_pct":72},     {"zone":"Koramangala","shadow_pct":50},
            {"zone":"Silk Board","shadow_pct":8},   {"zone":"Marathahalli","shadow_pct":12},
        ],
        "zone_aqi":[
            {"zone":"Lalbagh","aqi":72},  {"zone":"Cubbon","aqi":80},
            {"zone":"MG Road","aqi":112}, {"zone":"Indiranagar","aqi":125},
            {"zone":"Koramangala","aqi":135},{"zone":"Silk Board","aqi":188},
            {"zone":"Marathahalli","aqi":175},{"zone":"E-City","aqi":162},
        ],
        "heat_zones":HEAT_ZONES,"shade_zones":SHADE_ZONES,
    }

# ─── LANDMARKS ─────────────────────────────────
@app.get("/api/landmarks", tags=["City"])
async def landmarks():
    return {"city":"Bengaluru","count":len(LANDMARKS),"landmarks":LANDMARKS}

# ─── PROFILE ───────────────────────────────────
@app.get("/api/profile", tags=["User"])
async def profile():
    return {
        "user":{"name":"Shreyas Kumar","city":"Bengaluru","member_since":"2024"},
        "stats":{"walks":148,"km_shaded":62,"avg_cooler_c":3.2,"heat_avoidance_pct":89},
        "preferences":{
            "avoid_heat":True,"prefer_trees":True,"high_safety":True,
            "avoid_pollution":False,"low_crowd":False,"heat_alerts":True,
            "age":30,"speed_kmh":5,"heat_sensitivity":3,
        },
    }

@app.put("/api/profile/preferences", tags=["User"])
async def update_prefs(prefs: dict):
    return {"status":"updated","preferences":prefs}

# ─── SERVE FRONTEND ────────────────────────────
@app.get("/ui", tags=["Frontend"], response_class=HTMLResponse)
async def serve_ui():
    idx = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(idx):
        with open(idx, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h2>Place ShadeRoute_UI.html as frontend/index.html</h2>")
