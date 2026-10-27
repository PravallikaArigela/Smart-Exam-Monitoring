Task 1 — Understanding Examination Workflow

Step 1: Understand how an online examination works

An online examination system generally follows these steps:

Candidate Registration: The candidate creates an account with their name, email, password, and registration photo.
Candidate Login: The candidate logs in using their registered credentials.
Exam Instructions: The system displays examination rules and instructions.
Camera Initialization: The system requests camera access and checks whether the webcam works.
Examination Starts: The candidate begins the examination.
Face Monitoring: The system captures video frames and checks whether a face is visible.
Event Recording: The system records monitoring events, such as no face detected or multiple faces detected.
Exam Completion: The candidate submits the exam, and the session ends.
How your project fits into this workflow
Workflow stage	Technology
Registration and login	Flask
Candidate and session data	SQLite
Registration photo capture	OpenCV
Webcam video capture	OpenCV
Face detection	OpenCV
Synthetic test logs	Faker
Monitoring event storage	SQLite
Step 2: Identify integrity-monitoring requirements

Your system should monitor certain events during the examination.

No.	Requirement	Example
1	Camera availability	Webcam opens successfully
2	Face detection	One face is detected
3	Face absence	No face is detected for a period
4	Multiple-face detection	More than one face appears
5	Session tracking	Record when the exam session starts and ends
6	Event logging	Record the time and type of a monitoring event
7	Authentication	Only logged-in candidates can access protected pages
8	Error handling	Record camera failures or processing errors

Important: These events are indicators for review, not proof of cheating. For example, a candidate may look away from the screen or briefly move out of the camera's view for legitimate reasons.


Task 1: Study Online Examination Workflows and Integrity Monitoring Requirements

A. Objective

To understand the workflow of an online examination and identify the requirements needed to monitor examination sessions.

B. Examination Workflow

1. Candidate registers with personal details and a password.
2. Candidate logs in using registered credentials.
3. The system displays examination instructions.
4. The system initializes the webcam.
5. The candidate starts the examination.
6. OpenCV captures video frames and detects faces.
7. The system records relevant monitoring events.
8. The candidate submits the examination, and the session ends.

C. Functional Requirements

* Candidate registration and login.
* Secure password storage.
* Webcam initialization and video-frame capture.
* Face detection using OpenCV.
* Detection of frames containing no face or multiple faces.
* Examination session start and end tracking.
* Storage of monitoring events in SQLite.
* Generation of synthetic session logs using Faker for testing.
* Protection of examination pages through session authentication.

D. Non-Functional Requirements

* Reliable webcam operation.
* Reasonable frame-processing performance.
* Secure handling of candidate credentials.
* Consistent storage of session and monitoring data.
* Clear handling of camera and application errors.
* Protection of candidate photographs and examination records.

E. Technologies

* Python: Application programming.
* Flask: Web application and routing.
* SQLite: Database storage.
* Flask-SQLAlchemy: Database interaction.
* OpenCV: Webcam access, image processing, and face detection.
* Faker: Synthetic test data generation.

F. Monitoring Events

Examples of events that may be recorded include:

* Examination session started.
* Examination session ended.
* Camera unavailable.
* No face detected.
* Multiple faces detected.
* Face detected again after temporary absence.

Each event should include an appropriate timestamp and reference to the examination session.

G. Limitations and Considerations

Face detection does not identify a person's identity or establish that misconduct has occurred. Lighting, camera position, and movement can affect detection. Monitoring events should be treated as indicators for review rather than automatic proof of cheating.

Candidate photographs and monitoring records should be stored securely and accessed only by authorized users.

H. Outcome

The online examination workflow and the functional and non-functional monitoring requirements have been identified. These requirements will guide the system architecture and database design in Task 2.
