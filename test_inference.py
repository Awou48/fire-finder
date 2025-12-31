import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
import matplotlib.pyplot as plt

def weighted_binary_crossentropy(y_true, y_pred):
    bce = K.binary_crossentropy(y_true, y_pred)
    weight_vector = y_true * 20.0 + (1.0 - y_true) * 1.0
    weighted_bce = weight_vector * bce
    return K.mean(weighted_bce)

MODEL_PATH = "models/FireFinder_best_model.h5"
DATA_PATH = "data/processed/X_TRAIN_GRID.npy"
LABEL_PATH = "data/processed/Y_TRAIN_GRID.npy"

def run_test():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model tidak ditemukan di {MODEL_PATH}")
        print("   Jalankan modeling.ipynb dulu!")
        return

    print("⏳ Sedang memuat model AI...")
    
    try:
        model = load_model(MODEL_PATH, custom_objects={'weighted_binary_crossentropy': weighted_binary_crossentropy})
        print("✅ Model berhasil dimuat!")
    except Exception as e:
        print(f"❌ Gagal load model: {e}")
        return

    print("⏳ Memuat data sampel...")
    try:
        X_all = np.load(DATA_PATH)
        y_all = np.load(LABEL_PATH)
        
        X_all[:, :, :, :, 1] = X_all[:, :, :, :, 1] / 50.0 
        X_all[:, :, :, :, 2] = X_all[:, :, :, :, 2] / 20.0 
        
        sample_idx = -1
        for i in range(len(y_all)):
            if np.sum(y_all[i]) > 0:
                sample_idx = i
                break
        
        if sample_idx == -1:
            print("⚠️ Tidak ada sampel api di dataset (Dataset bersih). Mengambil sampel acak index 0.")
            sample_idx = 0
        else:
            print(f"🔥 Ditemukan sampel kebakaran di index {sample_idx}")

        input_data = X_all[sample_idx:sample_idx+1]
        ground_truth = y_all[sample_idx]

    except Exception as e:
        print(f"❌ Gagal load data: {e}")
        return

    print("🧠 Sedang memprediksi...")
    prediction = model.predict(input_data)
    
    pred_map = prediction[0, :, :, 0]
    
    print(f"📊 Statistik Prediksi:")
    print(f"   Max Probability: {np.max(pred_map):.4f}")
    print(f"   Avg Probability: {np.mean(pred_map):.4f}")
    
    threshold = 0.5
    if np.max(pred_map) > threshold:
        print("🚨 KESIMPULAN: TERDETEKSI POTENSI KEBAKARAN! (SIAGA 1)")
    else:
        print("✅ KESIMPULAN: Area Aman.")

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    
    ax[0].imshow(ground_truth[:, :, 0], cmap='Reds', vmin=0, vmax=1)
    ax[0].set_title("Kenyataan (Ground Truth)")
    
    im = ax[1].imshow(pred_map, cmap='Reds', vmin=0, vmax=1)
    ax[1].set_title("Prediksi AI")
    
    plt.colorbar(im, ax=ax[1], label='Probabilitas')
    plt.savefig("test_result.png")
    print("\n🖼️  Gambar hasil prediksi disimpan sebagai 'test_result.png'")
    print("   Silakan buka gambar tersebut untuk melihat kinerja AI.")

if __name__ == "__main__":
    run_test()