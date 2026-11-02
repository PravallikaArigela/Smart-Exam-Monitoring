import cv2
import psutil
import time

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open webcam.")
    raise SystemExit(1)

process = psutil.Process()
frame_count = 0
start_time = time.perf_counter()

print("Resource usage test started.")
print("Press Q in the webcam window to stop.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read webcam frame.")
        break

    # Simulate basic image processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_count += 1

    # Measure CPU and memory usage once per second
    elapsed = time.perf_counter() - start_time

    if elapsed >= 1:
        cpu_usage = process.cpu_percent()
        memory_mb = process.memory_info().rss / (1024 * 1024)

        print(
            f"Frames: {frame_count} | "
            f"CPU: {cpu_usage:.1f}% | "
            f"Memory: {memory_mb:.2f} MB"
        )

        start_time = time.perf_counter()

    cv2.putText(
        frame,
        f"Frames: {frame_count}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("ExamGuard Resource Usage Test", frame)

    if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
        break

camera.release()
cv2.destroyAllWindows()

print("Resource usage test completed.")
