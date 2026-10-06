# Butuh models/FireFinder_best_model.h5 dan data/processed/{X,Y}_TRAIN_GRID.npy di build context
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
RUN useradd -m -u 1000 user
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ api/
COPY models/FireFinder_best_model.h5 models/
COPY data/processed/X_TRAIN_GRID.npy data/processed/Y_TRAIN_GRID.npy data/processed/
COPY --from=frontend /app/frontend/dist frontend/dist
RUN chown -R user /app
USER user
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
