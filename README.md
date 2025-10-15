# Gesture → Teks + Suara by nijaru 🎮🖐️

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Enabled-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Author](https://img.shields.io/badge/Author-Nizaru--gpt-blueviolet)

Deteksi gesture tangan lewat kamera, lalu menampilkan teks di layar (kiri-atas) dan memutar suara TTS (Text-to-Speech). Menggunakan **MediaPipe**, **OpenCV**, **Pygame**, dengan TTS **gTTS** (online) dan fallback **pyttsx3** (offline).

> File utama: `main.py`

---

## 🧠 Ringkasan

Aplikasi ini membaca frame dari webcam, mendeteksi pose tangan dengan MediaPipe Hands, lalu mengklasifikasikan 4 gesture sederhana. Ketika sebuah gesture stabil selama beberapa frame, aplikasi akan:

1️⃣ Menampilkan frasa yang sesuai di overlay (kiri-atas)

2️⃣ Memutar audio frasa tersebut (prioritas MP3 dari gTTS; jika gagal, WAV dari pyttsx3)

---

## ✋ Peta Gesture → Frasa

| Gesture    | Ikon                       | Frasa           | File audio                                           |
| ---------- | -------------------------- | --------------- | ---------------------------------------------------- |
| Open palm  | 🖐                         | "Halo semuanya" | `audio/halo.mp3` atau `audio/halo.wav`               |
| Thumb only | 👍                         | "Nama aku"      | `audio/nama_aku.mp3` atau `audio/nama_aku.wav`       |
| Pinky only | 🤘 (kelingking saja)       | "Nizar"         | `audio/nizar.mp3` atau `audio/nizar.wav`             |
| Shaka      | 🤙 (ibu jari + kelingking) | "Salam kenal"   | `audio/salam_kenal.mp3` atau `audio/salam_kenal.wav` |

> **Catatan:** “Pinky only” berarti hanya kelingking terangkat, jari lain mengepal.

---

## 🧾 Cara Mengganti Nama

Nama default pada gesture **pinky only (🤘)** adalah **“Nizar”**.

Untuk menggantinya, buka file `main.py`, lalu ubah bagian `PHRASES` seperti ini:

```python
PHRASES = {
    "open": ("Halo semuanya", "halo.mp3"),
    "thumb_only": ("Nama aku", "nama_aku.mp3"),
    # ubah teks "Nizar" menjadi nama kamu
    "pinky_only": ("Aksa", "aksa.mp3"),
    "shaka": ("Salam kenal", "salam_kenal.mp3"),
}
```

Saat dijalankan setelah perubahan, program otomatis membuat file audio baru (`audio/aksa.mp3` atau `audio/aksa.wav`).

---

## ⚙️ Cara Kerja

* MediaPipe Hands mendeteksi 21 titik landmark per tangan.
* Fungsi `fingers_state()` menilai jari terangkat/turun.
* Gesture dikenali via kombinasi jari (`identify_gesture()`).
* Debounce: gesture harus stabil selama `DEBOUNCE_FRAMES` frame.
* Cooldown: waktu jeda agar tidak memicu ulang.
* Audio dibuat otomatis jika belum ada.

---

## 💻 Persyaratan Sistem

* Python 3.9+
* Webcam aktif
* Internet (untuk gTTS pertama kali)
* OS: Windows / macOS / Linux

---

## 🚀 Instalasi Cepat

```bash
# 1. Buat virtualenv (opsional)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 2. Instal dependensi
pip install --upgrade pip
pip install mediapipe opencv-python pygame gTTS pyttsx3

# 3. Jalankan (khusus Windows gunakan perintah ini)
py main.py
```

> ⚠️ Jika perintah `python main.py` menampilkan error seperti *“Python was not found”*, gunakan **`py main.py`** karena Windows menggunakan alias `py` untuk menjalankan Python versi terdaftar.

Tekan **`q`** di jendela kamera untuk keluar.

---

## 🧩 Konfigurasi Penting

```python
AUDIO_DIR = "audio"
DEBOUNCE_FRAMES = 6
COOLDOWN = 2.0
```

Ubah `PHRASES` untuk mengganti teks dan file audio.

---

## 🎙️ Kustomisasi Suara

**gTTS:** Bahasa default `id` (Indonesia). Bisa ubah ke `en`, `jp`, dll.

**pyttsx3:** Offline, bisa ubah voice & speed.

```python
engine = pyttsx3.init()
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\...')
engine.setProperty('rate', 180)
```

---

## 🧠 Tips Akurasi Gesture

* Gunakan pencahayaan terang.
* Hindari background kompleks.
* Jaga jarak ideal dari kamera (~40–70 cm).
* Jika sering error → naikkan `min_detection_confidence` ke `0.7`.

---

## 🧰 Troubleshooting

**Webcam tidak terbuka:** pastikan tidak dipakai aplikasi lain.

**Audio tidak keluar:** cek log `[AUDIO] Failed to play`.

**gTTS gagal:** coba tanpa internet → pyttsx3 otomatis digunakan.

**Perintah `python` error di Windows:** gunakan `py main.py`.

---

## 🧱 Struktur Proyek

```
project/
├─ main.py
└─ audio/
   ├─ halo.mp3|wav
   ├─ nama_aku.mp3|wav
   ├─ nizar.mp3|wav
   └─ salam_kenal.mp3|wav
```

---

## 🗺️ Roadmap Ide

* Tambah banyak gesture baru 🖖✊🤞
* Menu UI untuk pilih suara dan frasa.
* Logging statistik FPS.
* Integrasi model ML untuk klasifikasi gesture lebih kompleks.

---

## 📜 Lisensi

MIT License © 2025 — bebas digunakan & dimodifikasi.

---

## 👨‍💻 Author

Created with ❤️ by **[Nizaru-gpt](https://github.com/Nizaru-gpt)**

Jika kamu menggunakan proyek ini, jangan lupa kasih ⭐ di repo GitHub-nya!
