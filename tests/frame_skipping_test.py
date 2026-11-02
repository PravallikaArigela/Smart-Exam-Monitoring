import cv2
import time

# Open the webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open webcam.")
    raise SystemExit(1)

# Load Haar Cascade face detector
cascade_path = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

face_detector = cv2.CascadeClassifier(cascade_path)

if face_detector.empty():
    camera.release()
    raise RuntimeError("Could not load Haar Cascade detector.")

frame_number = 0
processed_frames = 0
skipped_frames = 0

detection_time_ms = 0.0

print("Frame skipping test started.")
print("Face detection runs on every third frame.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read webcam frame.")
        break

    frame_number += 1

    # Process every third frame
    if frame_number % 3 == 0:
        processing_start = time.perf_counter()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        detection_time_ms = (
            time.perf_counter() - processing_start
        ) * 1000

        processed_frames += 1

        # Draw bounding boxes on detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        status = f"Detection: {len(faces)} face(s)"

    else:
        skipped_frames += 1
        status = "Detection skipped"

    cv2.putText(
        frame,
        status,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Processed: {processed_frames}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Skipped: {skipped_frames}",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Detection time: {detection_time_ms:.2f} ms",
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2
    )

    cv2.imshow("Frame Skipping Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("\nFrame skipping test finished.")
print("Total frames captured:", frame_number)
print("Frames processed:", processed_frames)
print("Frames skipped:", skipped_frames)

