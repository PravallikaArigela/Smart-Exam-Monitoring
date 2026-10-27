import cv2
import os

# Folder where captured photos will be saved
PHOTO_FOLDER = os.path.join("app", "static", "photos")
os.makedirs(PHOTO_FOLDER, exist_ok=True)

# Open the webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open webcam.")
    raise SystemExit(1)

print("Webcam opened successfully!")
print("Press S to capture and save a photo.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Error: Could not read webcam frame.")
        break

    cv2.imshow("Candidate Registration Photo", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        photo_path = os.path.join(
            PHOTO_FOLDER,
            "test_candidate.jpg"
        )

        saved = cv2.imwrite(photo_path, frame)

        if saved:
            print(f"Photo saved successfully: {photo_path}")
        else:
            print("Error: Could not save photo.")

    elif key == ord("q"):
        break

# Release webcam resources
camera.release()
cv2.destroyAllWindows()

print("Webcam closed.")

