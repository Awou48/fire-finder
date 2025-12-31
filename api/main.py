import os
import random
import numpy as np
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.config import *
from api.utils import *
from api.database import init_db, get_db, FireLog
from api.evaluation import generate_confusion_matrix_image

app = FastAPI(title="FireFinder AI Ultimate", version="9.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Gemini
llm_model = None
if "ISI_API_KEY" not in GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        llm_model = genai.GenerativeModel('gemini-2.5-flash')
    except: pass

model = None
X_all = None
y_all = None
fire_indices = []

@app.on_event("startup")
async def startup():
    global model, X_all, y_all, fire_indices
    init_db()
    if os.path.exists(MODEL_PATH):
        try:
            model = load_model(MODEL_PATH, custom_objects={'weighted_binary_crossentropy': weighted_binary_crossentropy})
            print("✅ MODEL READY")
        except Exception as e: print(f"❌ MODEL ERROR: {e}")
            
    if os.path.exists(DATA_PATH):
        try:
            X_all = np.load(DATA_PATH)
            y_all = np.load(LABEL_PATH)
            sums = np.sum(y_all, axis=(1, 2, 3))
            fire_indices = np.where(sums > 0)[0].tolist()
            print(f"✅ DATA READY: {len(fire_indices)} samples")
        except: pass

@app.get("/predict/future")
def predict_future(days: int = Query(1), db: Session = Depends(get_db)):
    if model is None: raise HTTPException(503, "Loading...")
    try:
        num_points = random.randint(3, 6)
        daily_hotspots = []
        base_idx = (days * 19) % len(fire_indices)
        main_weather = None
        max_prob_global = 0

        for i in range(num_points):
            current_idx = fire_indices[(base_idx + i) % len(fire_indices)]
            input_data = X_all[current_idx:current_idx+1].copy()
            input_data[:, :, :, :, 1] /= 50.0
            input_data[:, :, :, :, 2] /= 20.0
            pred = model.predict(input_data, verbose=0)[0, :, :, 0]
            max_prob = float(np.max(pred))
            
            if max_prob > 0.45:
                flat_idx = np.argmax(pred)
                row, col = np.unravel_index(flat_idx, pred.shape)
                lat = MIN_LAT + (row * GRID_RES) + random.uniform(-0.1, 0.1)
                lon = MIN_LON + (col * GRID_RES) + random.uniform(-0.1, 0.1)
                level, color = "SIAGA", "yellow"
                if max_prob > 0.65: level, color = "WASPADA", "orange"
                if max_prob > 0.80: level, color = "BAHAYA", "red"
                region = get_kalimantan_region(lat, lon)
                
                if level == "BAHAYA":
                    weather = get_real_weather(lat, lon)
                    if max_prob > max_prob_global:
                        max_prob_global = max_prob
                        main_weather = weather
                    existing = db.query(FireLog).filter(FireLog.latitude==lat, FireLog.longitude==lon).first()
                    if not existing:
                        db.add(FireLog(latitude=lat, longitude=lon, region=region, confidence=round(max_prob*100, 2), level=level, temp=weather['temp'], wind=weather['wind']))
                        db.commit()

                daily_hotspots.append({"lat": lat, "lon": lon, "prob": round(max_prob*100, 1), "level": level, "color": color, "region": region})
        
        daily_hotspots.sort(key=lambda x: x['prob'], reverse=True)
        return {"prediction_day": f"H+{days}", "status_summary": "KRITIS" if any(h['level']=='BAHAYA' for h in daily_hotspots) else "WASPADA", "hotspots": daily_hotspots, "main_weather": main_weather or {"temp": "-", "wind": "-", "desc": "-"}}
    except Exception as e: return {"error": str(e)}

@app.get("/history")
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(FireLog).order_by(FireLog.timestamp.desc()).limit(limit).all()

@app.get("/performance/matrix")
def get_matrix_plot():
    if model is None or X_all is None: raise HTTPException(503, "Not ready")
    return generate_confusion_matrix_image(model, X_all, y_all)

class RouteRequest(BaseModel):
    target_lat: float
    target_lon: float

@app.post("/calculate-mission")
async def calculate_mission(payload: RouteRequest):
    print(f"\n📡 DEBUG MISI: Target Lat={payload.target_lat}, Lon={payload.target_lon}")
    if not FIRE_STATIONS: raise HTTPException(500, "DB Pos Kosong")
    nearest, min_dist_sq = None, float('inf')
    for s in FIRE_STATIONS:
        d = (s["lat"]-payload.target_lat)**2 + (s["lon"]-payload.target_lon)**2
        if d < min_dist_sq: min_dist_sq, nearest = d, s
    
    if nearest:
        dist_km = (min_dist_sq**0.5)*111
        return {"source": nearest, "target": payload, "distance_km": round(dist_km, 2), "eta_minutes": int((dist_km/150)*60)}
    raise HTTPException(404, "Pos not found")

class AdvisorPayload(BaseModel):
    summary_text: str

@app.post("/ask-advisor")
async def ask_advisor(payload: AdvisorPayload):
    if not llm_model: return {"reply": "Advisor Offline."}
    try:
        res = llm_model.generate_content(f"Komandan AI, Situasi: {payload.summary_text}. Instruksi taktis militer singkat:")
        return {"reply": res.text}
    except Exception as e: return {"reply": str(e)}