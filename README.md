# FireFinder AI

Course prototype that predicts next-day forest-fire hotspots in Kalimantan from the previous 7 days of satellite data (ConvLSTM), shown on a React + Leaflet dashboard.

> **Status: archived prototype.** It runs on historical **2023** data only. There is no live satellite feed. The model is not accurate enough to be trusted for real fire forecasting. See [Limitations](#limitations).

## Stack

- **Data pipeline / training:** Jupyter notebooks, NumPy, pandas, netCDF4, scikit-image, TensorFlow/Keras (`ConvLSTM2D`)
- **Backend:** FastAPI, SQLAlchemy (SQLite), OpenWeatherMap API, Google Gemini API (`google-generativeai`)
- **Frontend:** React 19, Vite, Tailwind CSS, Leaflet (`react-leaflet`), Axios

## How it works

```
FIRMS / MODIS / GPM files ─► notebooks ─► X_TRAIN_GRID.npy, Y_TRAIN_GRID.npy ─► modeling.ipynb ─► FireFinder_best_model.h5
                                                     │                                              │
                                                     └──────────────► FastAPI (api/) ◄──────────────┘
                                                                          │
                                                               React + Leaflet (frontend/)
```

**Input grid.** Kalimantan is rasterised at 0.25° (lat −5 → 5, lon 108 → 119.5, giving 40 × 46 cells). Each day has 4 channels:

| Channel | Source |
|---|---|
| 0 | Hotspot (0/1), NASA FIRMS |
| 1 | Land surface temperature, MODIS MOD11A1 (÷50 before inference) |
| 2 | Rainfall, GPM IMERG (÷20 before inference) |
| 3 | NDVI, MODIS MOD13A1 |

**Model.** The input is a 7-day window `(7, 40, 46, 4)`. The output is a fire probability per cell `(40, 46, 1)` for the next day. The network is two `ConvLSTM2D(32)` layers, then `Conv2D(16)` and `Conv2D(1, sigmoid)`. It is trained with binary cross-entropy that weights fire cells 20×. The data covers 2023-01-01 → 2023-12-31, giving 358 windows. The split is chronological 80/20.

**Notebooks** (run from `notebooks/`, in order):

1. `download_data.ipynb`: downloads GPM, MODIS LST/NDVI (and unused AOD/ERA5) for 2023. Needs NASA Earthdata credentials, entered in the notebook (don't commit them).
2. `preprocessing.ipynb`: merges the FIRMS CSV exports (`data/raw/fire_nrt_*.csv`, downloaded manually from FIRMS) into `data/processed/dataset_FireFinder_ai_kalimantan.csv`.
3. `grid_generation.ipynb`: builds `X_TRAIN_GRID.npy` `(358, 7, 40, 46, 4)` and `Y_TRAIN_GRID.npy` `(358, 40, 46, 1)`.
4. `modeling.ipynb`: trains the model and saves `models/FireFinder_best_model.h5`.

## Dashboard features

- **Map:** hotspot markers, coloured by level: `SIAGA` > 45%, `WASPADA` > 65%, `BAHAYA` > 80%.
- **Timeline slider H+1…H+7:** each position replays a different set of 2023 samples (see Limitations).
- **Weather panel:** current weather from OpenWeatherMap at the top `BAHAYA` hotspot. Without an API key it shows random estimates marked `(Est)`.
- **AI Command Center:** sends a short status summary to Gemini (`gemini-2.5-flash`) and shows the reply. Without a key it replies `Advisor Offline.`
- **Deploy drone:** finds the nearest of 5 hard-coded stations and draws a straight route with ETA (150 km/h, 1° ≈ 111 km).
- **Data logs:** `BAHAYA` predictions saved to SQLite (`firefinder.db`).
- **Evaluasi AI:** confusion matrix on the first 100 samples.

API endpoints: `GET /predict/future?days=N`, `GET /history?limit=N`, `GET /performance/matrix`, `POST /calculate-mission`, `POST /ask-advisor`. Interactive docs are at `/docs`.

## Required artifacts

These files are too large for GitHub and are git-ignored:

| File | Size | How to get it |
|---|---|---|
| `models/FireFinder_best_model.h5` | 1.5 MB | run `notebooks/modeling.ipynb` |
| `data/processed/X_TRAIN_GRID.npy` | 148 MB | run `notebooks/grid_generation.ipynb` |
| `data/processed/Y_TRAIN_GRID.npy` | 5 MB | run `notebooks/grid_generation.ipynb` |

The team shared the raw/processed data pack (`RESOURCES_AOL_AI.zip`) privately via Google Drive.
Without the model or the `.npy` files, the backend still starts but `/predict/future` and `/performance/matrix` return `503`.

## Run locally

Requires Python 3.12 and Node.js 20.19+.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env              # optional: add API keys
uvicorn api.main:app --port 8000  # run from the repo root
```

```bash
cd frontend
npm ci
npm run dev                       # http://localhost:5173, talks to http://127.0.0.1:8000
```

`test_inference.py` is a standalone check. It loads the model, predicts one fire sample and writes `test_result.png`.

### Environment variables

| Variable | Used by | Default / behaviour when empty |
|---|---|---|
| `OPENWEATHER_API_KEY` | backend | random weather estimates |
| `GEMINI_API_KEY` | backend, `cek_model.py` | advisor returns `Advisor Offline.` |
| `MODEL_PATH` | backend | `models/FireFinder_best_model.h5` |
| `VITE_API_URL` | frontend build | `http://127.0.0.1:8000` in dev, same origin in production builds |

## Checks

```bash
cd frontend && npm run lint && npm run build
```

There is no automated test suite. Manual check: start the backend, call every endpoint (or use `/docs`), then use each dashboard feature in the browser.

## Deployment

The `Dockerfile` builds the frontend and serves it from the FastAPI app on port 7860, so the app runs as a single container. The project is not currently deployed. The container fits a free CPU **Hugging Face Docker Space**. To deploy:

1. Put the three artifacts above into `models/` and `data/processed/`.
2. Upload the repo and the artifacts to a Docker Space. Its README needs `sdk: docker` and `app_port: 7860`.
3. Optional: set `GEMINI_API_KEY` / `OPENWEATHER_API_KEY` as Space secrets.

Local Docker check:

```bash
docker build -t firefinder .
docker run -p 7860:7860 --env-file .env firefinder
```

## Limitations

- **No real forecast.** `/predict/future` does not use current data. It takes 3–6 windows from the 2023 training tensors (offset by the slider value), runs the model, takes the max-probability cell of each, and adds ±0.1° random jitter. "H+N" only selects which historical samples are shown.
- **Weak model.** On the chronological validation split (last 20% of 2023), at threshold 0.5: recall ≈ 0.95, precision ≈ 0.07. It flags far more cells as fire than actually burn.
- **Retrained weights.** The originally trained `FireFinder_best_model.h5` was not preserved. The current file was regenerated by running `modeling.ipynb` unchanged on the same 2023 tensors, so numbers differ slightly from the notebook's saved output. An older `FireFinder_ai_model_v1.h5` from the team data pack (single ConvLSTM layer, trained without the LST/rain scaling) does not match the current preprocessing. Don't use it with this API.
- **Data alignment.** The LST, rain and NDVI rasters are resized to the grid without reprojection or cropping. Missing days are filled with constants.
- **Evaluation.** The in-app confusion matrix uses the first 100 samples, which are part of the training split.
- **Weather.** The weather panel shows today's weather (or random estimates), not 2023 conditions.
- **Advisor.** Gemini replies are free-form LLM text, not validated guidance. `google-generativeai` is deprecated, so the advisor may stop working if the model is retired.
- **Other.** Drone routes are straight lines between hard-coded stations. The SQLite log on the free host resets whenever the container restarts. The UI is Indonesian-only and has some layout awkwardness on small screens.

## Team

This repository houses our group's Artificial Intelligence course project. My specific technical contributions (@Awou48) included the FastAPI backend architecture, training the machine learning models, and building the interactive map interface, while my teammates drove the overall project execution. I welcome any of my teammates to use this repository for their portfolios!
