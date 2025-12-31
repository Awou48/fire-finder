import os

# 1. API KEYS
OPENWEATHER_API_KEY = "Nasa_pencariapi6"
GEMINI_API_KEY = "Nasa_pencariapi6"

# 2. KONFIGURASI FILE & MODEL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "FireFinder_best_model.h5")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "X_TRAIN_GRID.npy")
LABEL_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "Y_TRAIN_GRID.npy")

#  3. KONFIGURASI GRID PETA 
MIN_LAT = -5.0
MIN_LON = 108.0
GRID_RES = 0.25

#  4. DATABASE POS PEMADAM
# Data statis lokasi markas pemadam untuk fitur Rute Drone
FIRE_STATIONS = [
    {"id": "POS-01", "lat": -0.02, "lon": 109.33, "name": "HQ Pontianak (Air Unit)"},
    {"id": "POS-02", "lat": -2.53, "lon": 112.95, "name": "HQ Sampit (Drone Base)"},
    {"id": "POS-03", "lat": -1.25, "lon": 116.83, "name": "HQ Balikpapan (Rapid Response)"},
    {"id": "POS-04", "lat": -3.31, "lon": 114.59, "name": "HQ Banjarmasin (Water Bomber)"},
    {"id": "POS-05", "lat": 2.15, "lon": 117.49, "name": "HQ Berau (Support Unit)"}
]

#  5. DATABASE CONFIG 
DATABASE_URL = "sqlite:///./firefinder.db"