import cv2

# Load OpenCV's pre-trained face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Check whether the face detector loaded successfully
if face_cascade.empty():
    raise RuntimeError("Could not load the face detection model.")

# Open the webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open the webcam.")
    raise SystemExit

print("Face detection started!")
print("Press Q to exit.")

while True:
    # Capture a frame
    success, frame = camera.read()

    if not success:
        print("Could not read webcam frame.")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around each detected face
    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    # Display the number of detected faces
    cv2.putText(
        frame,
        f"Faces detected: {len(faces)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # Show the webcam feed
    cv2.imshow("Exam Monitoring - Face Detection", frame)

    # Exit when Q is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()

print("Face detection stopped.")
