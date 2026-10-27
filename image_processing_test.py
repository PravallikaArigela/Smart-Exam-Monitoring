import cv2
import os

file_path = os.path.abspath("sample.jpg")

print("Image path:", file_path)
print("File size:", os.path.getsize(file_path), "bytes")
print("Is a file:", os.path.isfile(file_path))
print("Current working directory:", os.getcwd())
print("Files in this folder:", os.listdir())

# 1. Load an image
image = cv2.imread("sample.jpg")

if image is None:
    print("Error: Could not load sample.jpg")
    print("Place an image named sample.jpg in the project folder.")
    raise SystemExit

# 2. Display image dimensions and channels
height, width = image.shape[:2]

print("Image width:", width)
print("Image height:", height)
print("Image dimensions:", image.shape)
print("Color channels:", image.shape[2])

# 3. Convert BGR to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 4. Resize the image
resized = cv2.resize(image, (640, 480))

# 5. Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(image, (5, 5), 0)

normalized = gray / 255.0

print("Original grayscale pixel range:", gray.min(), "to", gray.max())
print("Normalized pixel range:", normalized.min(), "to", normalized.max())

_, thresholded = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# 6. Display the results
cv2.imshow("Original Image", image)
cv2.imshow("Grayscale Image", gray)
cv2.imshow("Resized Image", resized)
cv2.imshow("Gaussian Blur", blurred)
cv2.imshow("Normalized Image", normalized)
cv2.imshow("Thresholded Image", thresholded)

print("Press Q on an image window to close the program.")

cv2.waitKey(0)
cv2.destroyAllWindows()

