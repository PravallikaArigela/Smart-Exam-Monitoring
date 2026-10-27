import cv2
import time

# Open the default webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open the webcam.")
    raise SystemExit

print("Webcam opened successfully!")
print("Press Q to close the webcam window.")

while True:
    start_time = time.perf_counter()

    # Capture one frame from the webcam
    success, frame = camera.read()

    if not success:
        print("Error: Could not read a frame.")
        break

    # Calculate frame-processing time
    processing_time = (time.perf_counter() - start_time) * 1000

    # Display processing time on the video
    cv2.putText(
        frame,
        f"Processing time: {processing_time:.2f} ms",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Display the live webcam feed
    cv2.imshow("Exam Monitoring - Webcam Test", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and close windows
camera.release()
cv2.destroyAllWindows()

print("Webcam closed.")
