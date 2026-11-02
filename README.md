# ExamGuard – Smart Online Examination Monitoring System

## 1. Project Overview

ExamGuard is a web-based online examination monitoring system developed using Python, Flask, SQLite, and OpenCV.

The system provides candidate authentication, examination session management, and webcam-based face monitoring to support the integrity of online examinations.

It uses computer vision techniques to detect faces and identify basic monitoring events during an examination.

## 2. Key Features

* Candidate registration and login.
* Secure password storage.
* Examination session creation and management.
* Webcam access using OpenCV.
* Face detection using Haar Cascade Classifier.
* Face monitoring during examinations.
* Detection of face absence and multiple faces.
* Camera failure and detection failure handling.
* Automatic session interruption detection using heartbeat monitoring.
* Automatic webcam shutdown when an examination session is interrupted.
* Monitoring event storage in SQLite.
* Synthetic monitoring log generation using Faker.

## 3. Technologies Used

| Technology   | Purpose                        |
| ------------ | ------------------------------ |
| Python       | Backend programming            |
| Flask        | Web application framework      |
| SQLite       | Database                       |
| SQLAlchemy   | Database management            |
| OpenCV       | Image and video processing     |
| Haar Cascade | Face detection                 |
| Faker        | Synthetic test data generation |
| HTML/CSS     | Frontend development           |
| JavaScript   | Heartbeat communication        |

## 4. Project Structure

```text
ExamGuard/
│
├── app/
│   ├── templates/
│   ├── __init__.py
│   ├── face_monitor.py
│   ├── models.py
│   └── routes.py
│
├── tests/
│   ├── camera_unavailable_test.py
│   ├── capture_photo.py
│   ├── face_detection.py
│   ├── fps_test.py
│   ├── frame_skipping_test.py
│   ├── generate_logs.py
│   ├── image_processing_test.py
│   ├── resource_usage_test.py
│   └── other test scripts
│
├── instance/
│   └── eam_monitoring.db
│
├── config.py
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: The database file is created or maintained in the instance folder. Actual test filenames may vary.*

## 5. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/PravallikaArigela/Smart-Exam-Monitoring.git
```

### Step 2: Open the Project Folder

```bash
cd Smart-Exam-Monitoring
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Running the Application

Start the Flask application:

```bash
python run.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Register a candidate account or log in using an existing account.

## 7. Examination Workflow

1. Candidate registers or logs into the application.
2. Candidate opens the dashboard.
3. Candidate starts an examination.
4. The webcam is accessed using OpenCV.
5. Haar Cascade detects faces in webcam frames.
6. Monitoring events are recorded during the examination.
7. Heartbeat monitoring checks browser activity.
8. If browser activity stops for more than the configured timeout, the session is marked as interrupted.
9. Face monitoring stops when the examination session becomes inactive.
10. Examination details and monitoring events are stored in SQLite.

## 8. Database Structure

The application uses SQLite with three main tables.

### Candidates

Stores candidate registration and authentication information, including profile photo data.

### Exam Sessions

Stores examination session information, including:

* Candidate ID
* Start time
* End time
* Session status
* Last heartbeat

### Monitoring Events

Stores monitoring activities such as:

* session_started
* session_ended
* session_interrupted
* face_present
* face_absent
* multiple_faces
* camera_unavailable
* detection_failure
* camera_read_failure

## 9. Testing and Validation

The following practical tests were performed:

* Webcam access and frame capture.
* Haar Cascade face detection.
* Image preprocessing.
* Grayscale conversion.
* Thresholding and normalization.
* FPS and processing latency measurement.
* Frame skipping.
* Resource usage measurement.
* Camera unavailable handling.
* Face detection failure handling.
* Camera read failure handling.
* Automatic session interruption.
* Normal examination completion.
* Database record verification.

## 10. Current Project Status

The main Flask application, database integration, webcam access, face detection, and examination session management have been implemented and tested.

Both normal examination completion and automatic session interruption have been verified through database records.

## 11. Future Enhancements

* Improve face detection under different lighting conditions.
* Integrate more advanced face recognition techniques.
* Add additional examination integrity checks.
* Develop a detailed monitoring dashboard.
* Improve reporting and examination analytics.
* Strengthen application security and validation.

## 12. Conclusion

ExamGuard demonstrates the integration of web development, database management, and computer vision for online examination monitoring.

The project provides a foundation for monitoring candidate activity through webcam-based face detection and examination session management.
