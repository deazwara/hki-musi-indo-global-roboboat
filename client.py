import socket
import cv2
import struct
import time

SERVER_IP = "192.168.0.1" # Sesuaikan dengan ip server
SERVER_PORT = 8485

def main():
    print("Menghubungkan ke server...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("Terhubung ke server.")

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame tidak terbaca.")
            continue

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data = buffer.tobytes()
        size = len(data)

        timestamp = time.time()
        packet = struct.pack(">Ld", size, timestamp) + data
        sock.sendall(packet)

    cap.release()
    sock.close()

if __name__ == "__main__":
    main()
