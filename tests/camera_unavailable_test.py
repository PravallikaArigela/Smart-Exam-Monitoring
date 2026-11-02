import cv2

print("Testing webcam availability...")

camera = cv2.VideoCapture(99)

if not camera.isOpened():
    camera.release()
    print("SUCCESS: Camera unavailable was detected.")
else:
    camera.release()
    print("Camera opened. The test camera index may be available.")

print("Test completed.")

