# 🔥 FireFinder AI: Prediksi Kebakaran Hutan Kalimantan

Project ini menggunakan Deep Learning (ConvLSTM) untuk memprediksi lokasi titik api di Kalimantan berdasarkan data satelit (Hotspot, Suhu, Hujan, Vegetasi).

## 📂 Struktur Folder
Agar kode berjalan lancar, pastikan struktur folder di laptop kalian seperti ini:

AOL_AI/
│
├── notebooks/                  <-- (Kodingan dari GitHub)
│   ├── grid_generation.ipynb
│   ├── modeling.ipynb
│   └── (File lainnya boleh diabaikan)
│
├── data/
│   └── processed/              <-- TARUH FILE CSV DISINI
│       └── dataset_FireFinder_ai_kalimantan.csv
│
├── models/                     <-- TARUH FILE MODEL DISINI
│   └── FireFinder_ai_model_v1.h5
│
└── README.md

---

## 🚀 Cara Mulai (Quick Start)

### 1. Download Data Pack
1.  Download file **`RESOURCES_AOL_AI.zip`** dari Link Google Drive.
2.  Ekstrak isinya.
3.  Pindahkan file **`.csv`** ke folder `data/processed/`.
4.  Pindahkan file **`.h5`** ke folder `models/`.

### 2. Jalankan Grid Generation (`grid_generation.ipynb`) 🗺️
* **Wajib dijalankan pertama kali.**
* Notebook ini akan mengubah file CSV menjadi data gambar (Grid) untuk AI.
* **Output:** Akan muncul file `X_TRAIN_GRID.npy` dan `Y_TRAIN_GRID.npy` di folder `data/processed/`.

### 3. Jalankan Modeling (`modeling.ipynb`) 🤖
* Sekarang kalian bisa melatih ulang model atau melakukan evaluasi.
* Karena file `.npy` sudah terbentuk di langkah sebelumnya, kode ini akan jalan lancar.

---

## ℹ️ Info Dataset
Dataset yang digunakan (`dataset_FireFinder_ai_kalimantan.csv`) adalah data bersih tahun 2023 yang berisi:
* 🔥 **Hotspot:** Titik api asli (FIRMS).
* 🌡️ **LST:** Suhu tanah asli (MODIS).
* 🌧️ **Rainfall:** Curah hujan asli (GPM).
* 🌿 **NDVI:** Vegetasi interpolasi (MODIS).

Selamat mencoba! 🚀
