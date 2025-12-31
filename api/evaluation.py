import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from io import BytesIO
from fastapi.responses import StreamingResponse
import numpy as np

def generate_confusion_matrix_image(model, X_all, y_all):
    try:
        # Ambil sampel evaluasi (100 data)
        limit = min(100, len(X_all))
        X_test = X_all[:limit].copy()
        y_true_grid = y_all[:limit].copy()

        # Normalisasi
        X_test[:, :, :, :, 1] /= 50.0
        X_test[:, :, :, :, 2] /= 20.0

        # Prediksi
        y_pred_grid = model.predict(X_test, verbose=0)

        # Flattening (2D -> 1D)
        y_true_flat = (y_true_grid.flatten() > 0.5).astype(int)
        y_pred_flat = (y_pred_grid.flatten() > 0.5).astype(int)

        # Matriks
        cm = confusion_matrix(y_true_flat, y_pred_flat)

        # Plotting
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', cbar=False,
                    xticklabels=['Aman', 'Kebakaran'],
                    yticklabels=['Aman', 'Kebakaran'])
        plt.xlabel('Prediksi AI')
        plt.ylabel('Ground Truth')
        plt.title('Evaluasi Model (100 Sampel)')
        plt.tight_layout()

        # Save to Buffer
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        print(f"Plot Error: {e}")
        return None