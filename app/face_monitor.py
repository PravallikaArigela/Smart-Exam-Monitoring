import cv2
from datetime import datetime, timezone

from app import db
from app.models import ExamSession, MonitoringEvent


def monitor_exam(session_id):
    """Monitor webcam frames and record face monitoring events."""

    exam = db.session.get(ExamSession, session_id)

    if exam is None or exam.status != "active":
        return False, "No active exam session found."

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    if face_cascade.empty():
        return False, "Could not load the face detection model."

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        try:
            db.session.add(
                MonitoringEvent(
                    session_id=session_id,
                    event_type="camera_unavailable",
                    event_time=datetime.now(timezone.utc),
                    details="The webcam could not be opened."
                )
            )
            db.session.commit()
            
        except Exception:
            db.session.rollback()
            return False, "Webcam unavailable; event logging failed."
        
        return False, "Could not open the webcam."

    previous_event = None

    try:
        while True:
            
            db.session.expire_all()
            exam = db.session.get(ExamSession, session_id)
            
            if exam is None or exam.status != "active":
                print("Exam ended. Stopping face monitoring...")
                break
            
            success, frame = camera.read()

            if not success:
                event_type = "camera_read_failure"

                if previous_event != event_type:
                    db.session.add(
                        MonitoringEvent(
                            session_id=session_id,
                            event_type=event_type,
                            details="Could not read a webcam frame."
                        )
                    )
                    db.session.commit()
                    previous_event = event_type

                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            try:
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

            except cv2.error as error:
                try:
                    db.session.add(
                        MonitoringEvent(
                            session_id=session_id,
                            event_type="detection_failure",
                            event_time=datetime.now(timezone.utc),
                            details=f"Face detection failed: {error}"
                        )
                    )
                    db.session.commit()

                except Exception:
                    db.session.rollback()

                print(f"Face detection failed: {error}")
                break

            face_count = len(faces)

            if face_count == 0:
                event_type = "face_absent"
                details = "No face detected in the current frame."
            elif face_count == 1:
                event_type = "face_present"
                details = "One face detected."
            else:
                event_type = "multiple_faces"
                details = f"{face_count} faces detected."

            # Record only changes in event type to avoid
            # inserting a database row for every video frame.
            if event_type != previous_event:
                db.session.add(
                    MonitoringEvent(
                        session_id=session_id,
                        event_type=event_type,
                        event_time=datetime.now(timezone.utc),
                        details=details
                    )
                )
                db.session.commit()
                previous_event = event_type

            for (x, y, w, h) in faces:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            cv2.putText(
                frame,
                f"Faces detected: {face_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("ExamGuard Face Monitoring", frame)
            
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == ord("Q"):
                print("Q pressed. Stopping face monitoring...")
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    return True, "Face monitoring stopped."
