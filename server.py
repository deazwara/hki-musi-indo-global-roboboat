import socket
import struct
import time
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================
MODEL_PATH = "v8n.pt"
CONF_THRESHOLD = 0.60

IP = "0.0.0.0"
PORT = 8485

# =====================================================
# LOAD MODEL
# =====================================================
print("Loading YOLOv8 model:", MODEL_PATH)
model = YOLO(MODEL_PATH)
print("Model loaded successfully.")

# =====================================================
# SETUP TCP SERVER
# =====================================================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(1)

print(f"Menunggu koneksi di {IP}:{PORT} ...")
conn, addr = sock.accept()
print("Client terhubung dari:", addr)

# =====================================================
# LOG FILE SETUP (CSV, nama sesuai timestamp)
# =====================================================
start_dt = datetime.now()
start_ts_str = start_dt.strftime("%Y%m%d_%H%M%S")
log_filename = f"log_yolov8_tcp_detect_{start_ts_str}.csv"

print("Log file:", log_filename)

with open(log_filename, "w", encoding="utf-8") as f:
    f.write("# YOLOv8 TCP Detection Log\n")
    f.write(f"# Model: {MODEL_PATH}\n")
    f.write(f"# Start: {start_dt.isoformat()}\n\n")
    f.write("frame,fps,latency_ms,timestamp,num_detections,detections\n")

# =====================================================
# HELPER: RECV EXACT N BYTES
# =====================================================
def recvall(sock, length):
    data = b""
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

# =====================================================
# STATISTIC VARIABLES
# =====================================================
frame_count = 0
start_time = time.time()
fps_values = []
latency_values = []

# =====================================================
# MAIN LOOP (DETECTION-ONLY)
# =====================================================
while True:
    # ===== Terima header: size (4 byte) + timestamp (8 byte) =====
    header = recvall(conn, 12)
    if header is None:
        print("Client terputus (header).")
        break

    frame_size, client_timestamp = struct.unpack(">Ld", header)

    # ===== Terima data JPEG =====
    jpeg_data = recvall(conn, frame_size)
    if jpeg_data is None:
        print("Client terputus (frame).")
        break

    # Decode ke BGR
    frame = cv2.imdecode(np.frombuffer(jpeg_data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        print("Frame decode gagal.")
        continue

    # =================================================
    # INFERENCE YOLOv8
    # =================================================
    t0 = time.time()
    results = model(frame, conf=CONF_THRESHOLD, verbose=False)
    t1 = time.time()

    inference_ms = (t1 - t0) * 1000.0
    latency_values.append(inference_ms)

    detections = results[0]

    # =================================================
    # DRAW DETECTIONS + KUMPULKAN DATA UNTUK LOG
    # =================================================
    det_list = []

    for box in detections.boxes:
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        if conf < CONF_THRESHOLD:
            continue

        cls_name = detections.names[cls]
        det_list.append((cls_name, conf))

        # Warna kotak: sampah = merah, lainnya = hijau
        if cls_name.lower() == "sampah":
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"{cls_name} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # =================================================
    # FPS CALC
    # =================================================
    frame_count += 1
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0.0
    fps_values.append(fps)

    # =================================================
    # LOG KE CSV
    # =================================================
    now_ts = time.time()
    detections_str = "[" + ",".join(
        f"('{name}',{conf:.2f})" for name, conf in det_list
    ) + "]"

    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(
            f"{frame_count},{fps:.2f},{inference_ms:.2f},{now_ts:.6f},"
            f"{len(det_list)},\"{detections_str}\"\n"
        )

    # =================================================
    # OVERLAY INFO DI DISPLAY
    # =================================================
    time_str = datetime.now().strftime("%H:%M:%S")

    cv2.putText(frame, f"FPS: {fps:.2f}",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)

    cv2.putText(frame, f"Latency: {inference_ms:.2f} ms",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 255), 2)

    cv2.putText(frame, f"Time: {time_str}",
                (10, 75), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2)

    cv2.imshow("YOLOv8 TCP Detection", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        print("ESC ditekan, keluar loop.")
        break

# =====================================================
# SUMMARY STATISTICS
# =====================================================
end_dt = datetime.now()
print("Sesi selesai pada:", end_dt.isoformat())

with open(log_filename, "a", encoding="utf-8") as f:
    f.write(f"\n# End: {end_dt.isoformat()}\n")

if fps_values and latency_values:
    fps_avg = sum(fps_values) / len(fps_values)
    fps_min = min(fps_values)
    fps_max = max(fps_values)

    lat_avg = sum(latency_values) / len(latency_values)
    lat_min = min(latency_values)
    lat_max = max(latency_values)

    print("===== RINGKASAN =====")
    print(f"FPS AVG : {fps_avg:.2f}")
    print(f"FPS MIN : {fps_min:.2f}")
    print(f"FPS MAX : {fps_max:.2f}")
    print(f"LAT AVG : {lat_avg:.2f} ms")
    print(f"LAT MIN : {lat_min:.2f} ms")
    print(f"LAT MAX : {lat_max:.2f} ms")

    with open(log_filename, "a", encoding="utf-8") as f:
        f.write("\nsummary_type,fps_avg,fps_min,fps_max,lat_avg,lat_min,lat_max\n")
        f.write(
            "summary,"
            f"{fps_avg:.4f},{fps_min:.4f},{fps_max:.4f},"
            f"{lat_avg:.4f},{lat_min:.4f},{lat_max:.4f}\n"
        )

# Cleanup
conn.close()
sock.close()
cv2.destroyAllWindows()

print("Log tersimpan di:", log_filename)
