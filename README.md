# Musi Indo Global Roboboat: Sistem Persepsi Deteksi Sampah

Sistem persepsi berbasis computer vision untuk mendeteksi objek sampah
pada lingkungan perairan secara real-time menggunakan model YOLOv8n
dengan arsitektur client—server berbasis TCP dalam jaringan lokal
(LAN).

------------------------------------------------------------------------

## 📌 Deskripsi Singkat

Program ini dirancang untuk mendeteksi dua kelas objek, yaitu:

-   `sampah`
-   `bukan_sampah`

Sistem menggunakan Raspberry Pi sebagai perangkat client untuk menangkap
video dari webcam dan mengirimkan frame ke server melalui komunikasi
TCP. Proses inferensi dilakukan pada sisi server menggunakan GPU.

Hasil deteksi ditampilkan secara real-time dalam bentuk bounding box,
label kelas, confidence score, FPS, serta waktu inferensi. Sistem juga
menghasilkan log performa dalam format CSV.

------------------------------------------------------------------------

## 🏗 Arsitektur Sistem

Webcam (Logitech C270)
↓
Raspberry Pi 4 (Client)
- Capture 640x480
- JPEG Encode
- TCP Send
  
Laptop/PC (Server)
- Receive Frame
- Decode JPEG
- YOLOv8 Inference (GPU)
- Display GUI
- Logging CSV

⚠ Sistem dirancang untuk berjalan dalam **satu jaringan lokal (LAN)**.

------------------------------------------------------------------------

## ⚙ Perangkat yang Digunakan dalam Pengujian

### 🖥 Server (Laptop)

-   OS: Windows 10 Home 64-bit
-   Processor: Intel Core i7-10750H
-   RAM: 16 GB
-   GPU: NVIDIA GeForce GTX 1660 Ti (6GB Dedicated VRAM)
-   DirectX 12

### 🍓 Client

-   Raspberry Pi 4 Model B
-   Webcam Logitech C270 (USB)
-   Resolusi input: 640 × 480

------------------------------------------------------------------------

## 🚀 Cara Menjalankan Program

### 1️⃣ Pastikan Dalam Satu Jaringan

Pastikan Raspberry Pi dan server (laptop/PC) berada dalam jaringan lokal
(LAN) yang sama.

### 2️⃣ Jalankan Server

Pada laptop/PC:

    python server.py

Server akan membuka socket TCP dan menunggu koneksi dari client.

### 3️⃣ Konfigurasi dan Jalankan Client

Pada Raspberry Pi:

1.  Buka `client.py`
2.  Ubah `SERVER_IP` sesuai dengan IP address laptop/server
3.  Jalankan:

```    python client.py

Client akan mengaktifkan webcam, mengatur resolusi 640x480, mengompresi
frame menjadi JPEG, dan mengirimkan frame ke server melalui TCP.

### 4️⃣ Tampilan GUI

Jika koneksi berhasil, GUI akan muncul pada sisi server dan
menampilkan: - Bounding box - Label kelas (`sampah` / `bukan_sampah`) -
Confidence score - FPS - Waktu inferensi (ms)

Tekan `ESC` untuk menghentikan program.

### 5️⃣ Log Hasil

Setelah program selesai dijalankan, sistem akan menghasilkan file log
dalam format `.csv` yang berisi: - Nomor frame - FPS - Waktu inferensi
(ms) - Timestamp - Jumlah deteksi - Daftar objek terdeteksi - Ringkasan
statistik

------------------------------------------------------------------------

## 📂 Struktur File

    server.py
    client.py
    v8n.pt
    README.md

------------------------------------------------------------------------

## ⚠ Batasan Sistem

-   Hanya berjalan dalam jaringan lokal (LAN)
-   Tidak mendukung komunikasi melalui internet publik
-   Tidak mencakup sistem navigasi atau kontrol gerak robot
-   Model yang digunakan: YOLOv8n

------------------------------------------------------------------------

## 🎯 Tujuan Pengembangan

Proyek ini dikembangkan sebagai bagian dari penelitian sistem persepsi
untuk robot pembersih sampah berbasis kecerdasan buatan, guna
membuktikan bahwa implementasi deteksi objek real-time pada platform
robot perairan memungkinkan dilakukan menggunakan arsitektur
terdistribusi berbasis TCP.
