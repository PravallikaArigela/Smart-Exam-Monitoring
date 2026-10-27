import cv2
import time

# Open the default webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open webcam.")
    raise SystemExit(1)

print("Webcam opened successfully!")
print("Press Q to quit.")

# FPS calculation variables
frame_count = 0
start_time = time.perf_counter()
fps = 0.0

# Frame processing latency
latency_ms = 0.0

while True:
    # Measure the time taken to capture a frame
    capture_start = time.perf_counter()

    success, frame = camera.read()

    capture_end = time.perf_counter()

    if not success:
        print("Error: Could not read frame.")
        break

    # Measure the time taken for basic frame processing
    processing_start = time.perf_counter()

    # Convert frame from BGR to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    processing_end = time.perf_counter()

    # Calculate processing latency in milliseconds
    latency_ms = (processing_end - processing_start) * 1000

    # Count frames for FPS calculation
    frame_count += 1
    elapsed_time = time.perf_counter() - start_time

    if elapsed_time >= 1.0:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.perf_counter()

    # Display FPS and latency on the preview
    cv2.putText(
        frame,
        f"FPS: {fps:.2f}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Processing latency: {latency_ms:.2f} ms",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2
    )

    cv2.imshow("FPS and Latency Test", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()

print("Webcam closed successfully.")

