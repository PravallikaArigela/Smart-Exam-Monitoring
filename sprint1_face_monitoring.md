Sprint 1: Face-Monitoring Architecture and Event Specification

1. Objective

The objective of this sprint is to design a face-monitoring system for an online examination application using OpenCV and Python.

The system captures webcam frames, preprocesses images, detects faces, measures basic processing performance, and defines monitoring events for examination integrity.

2. System Architecture

The proposed system contains the following components:

1. Candidate Authentication: Identifies the logged-in candidate.
2. Examination Session Management: Creates and tracks examination sessions.
3. Webcam Capture: Acquires video frames from the candidate's camera.
4. Image Preprocessing: Converts frames to grayscale and resizes them when necessary.
5. Face Detection: Uses OpenCV Haar Cascade to detect faces.
6. Event Classification: Determines whether zero, one, or multiple faces were detected.
7. Event Recording: Stores monitoring events in SQLite.
8. Session Termination: Releases the camera and updates the examination session status.

3. Image Processing

# Image Acquisition

Image acquisition is the process of obtaining an image from a webcam or image file.

# Pixels and Channels

A digital image consists of pixels. Each pixel stores information about the image's appearance. Color images commonly contain three channels.

# RGB and BGR

RGB represents red, green, and blue channels. OpenCV commonly represents color images in BGR order.

# Grayscale Conversion

Grayscale conversion represents an image using intensity values rather than separate color channels. Haar Cascade face detection commonly operates on grayscale images.

# Image Resizing

Resizing changes the dimensions of an image. Processing smaller images can improve performance but may reduce the visibility of facial details.

# Image Normalization

Normalization adjusts image values to a consistent numerical range or distribution. It is useful in some image-processing and machine-learning pipelines but is not mandatory for every Haar Cascade workflow.

# Image Filtering and Noise Reduction

Filtering can reduce image noise and unwanted variations. Excessive filtering can also remove useful facial details.

# Image Thresholding

Thresholding separates pixels according to intensity values. It can support certain image-segmentation tasks but is not required for every face-detection pipeline.

4. Video Processing

# Video Stream

A video stream is a sequence of frames captured over time.

# Webcam Capture and Frame Extraction

OpenCV captures webcam frames using VideoCapture. Each successful read produces an individual frame for processing.

# Frames Per Second

FPS represents the number of frames processed or displayed per second, depending on the measurement method.

# Real-Time Processing

Real-time processing captures and analyzes frames while the camera is running.

# Frame Skipping

Frame skipping reduces processing workload by running face detection on selected frames rather than every captured frame.

# Processing Latency

Processing latency measures the time required for a defined operation or sequence of operations. The measurement should clearly state which operations are included.

# Resource Utilization

CPU usage, memory consumption, frame rate, and processing time can help assess the system's performance.

5. Face Detection

# Face Detection versus Face Recognition

Face detection identifies the locations of faces in an image. Face recognition attempts to identify or verify a person.

# Detection Pipeline

The proposed pipeline captures a frame, preprocesses it, detects faces, evaluates the result, and generates an appropriate monitoring event.

# Bounding Boxes

A bounding box identifies the location of a detected face using its horizontal and vertical coordinates, width, and height.

# Confidence Scores and Detection Thresholds

Some face detectors provide confidence scores that estimate the strength of a detection. Haar Cascade commonly uses parameters such as scaleFactor and minNeighbors rather than exposing a calibrated probability for each detection.

# Haar Cascade

Haar Cascade is a traditional object-detection approach that uses learned visual patterns and a cascade of classifiers.

# DNN-Based Detection

Deep neural network detectors can learn more complex facial patterns. Their performance depends on the model, hardware, input resolution, and environmental conditions.

6. Monitoring Event Specification

| Event Type           | Definition                                      |
| -------------------- | ----------------------------------------------- |
| face_present         | Exactly one face is detected                    |
| face_absent          | No face is detected                             |
| multiple_faces       | More than one face is detected                  |
| detection_failure    | Image processing or face detection fails        |
| camera_unavailable   | The webcam cannot be opened                     |
| session_interruption | The active monitoring stream unexpectedly stops |

Each recorded event should contain an event ID, examination-session ID, event type, timestamp, and optional details.

# Event Recording Rules

* Record event-state changes rather than writing a new record for every frame.
* Define a configurable time interval before confirming a face-absent condition.
* Record camera and processing errors when they occur.
* Associate events with the correct examination session.
* Distinguish normal examination completion from an unexpected interruption.
* Treat detections as observations that may be incorrect, not definitive proof of misconduct.

7. Computer Vision Limitations

# Poor Lighting

Low light can reduce image quality and affect face detection.

# Camera Angle

Extreme camera angles can make facial features harder to detect.

# Occlusion

Masks, hands, hair, or other objects may partially cover the face.

# Low Resolution

Small or blurry faces may be difficult to detect.

# False Positives and False Negatives

A false positive occurs when the detector reports a face where no face is present. A false negative occurs when a real face is not detected.

# Different Skin Tones

Lighting, camera characteristics, image quality, and model design can contribute to differences in detection performance. The system should be evaluated across diverse users and conditions.

# Accessibility

Candidates may need accommodations for disability, assistive devices, or other circumstances that affect camera-based monitoring.

# Privacy

The application should explain what data is collected, why it is collected, how long it is retained, and who can access it. Access to photos and monitoring logs should be restricted.

8. Current Practical Progress

The following components have been tested independently:

* OpenCV installation and webcam access.
* Local webcam preview.
* Haar Cascade face detection.
* Registration photo capture.
* Grayscale conversion.
* FPS measurement.
* Basic frame-processing latency measurement.
* Frame skipping.

The Flask application also contains candidate, examination-session, and monitoring-event database models. Faker has been used to generate synthetic session and monitoring-event records.

9. Remaining Integration Work

The following work remains before the complete monitoring workflow can be considered functional:

* Integrate live face detection with the Flask examination session.
* Record real monitoring events from live detection results.
* Implement reliable camera-failure and stream-interruption handling.
* Apply event timing and state-change rules.
* Test resource usage and performance under representative conditions.
* Validate detection limitations, accessibility, and privacy controls.

10. Expected Sprint 1 Output

The expected output is a documented face-monitoring architecture and event specification, supported by independent practical tests of webcam access, face detection, FPS, processing latency, and frame skipping.
