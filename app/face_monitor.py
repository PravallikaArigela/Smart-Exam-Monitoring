import cv2
import threading

from datetime import datetime, timezone

from app import db
from app.models import ExamSession, MonitoringEvent


# Store active monitoring threads and stop signals.
monitoring_threads = {}
monitoring_events = {}

monitoring_lock = threading.Lock()


def record_event(session_id, event_type, details):
    """Save a monitoring event for the specified exam session."""

    db.session.add(
        MonitoringEvent(
            session_id=session_id,
            event_type=event_type,
            event_time=datetime.now(timezone.utc),
            details=details
        )
    )

    db.session.commit()


def start_monitoring(session_id):
    """Start face monitoring in a background thread."""

    with monitoring_lock:

        # Check whether monitoring is already running.
        if session_id in monitoring_threads:
            if monitoring_threads[session_id].is_alive():
                return False, "Monitoring is already running."

            monitoring_threads.pop(session_id, None)
            monitoring_events.pop(session_id, None)

        exam = db.session.get(ExamSession, session_id)

        if exam is None or exam.status != "active":
            return False, "No active exam session found."

        stop_event = threading.Event()

        exam.monitoring_status = "running"

        record_event(
            session_id,
            "monitoring_started",
            "Face monitoring started."
        )

        app = __import__("flask").current_app._get_current_object()

        thread = threading.Thread(
            target=monitor_exam,
            args=(app, session_id, stop_event),
            daemon=True
        )

        monitoring_threads[session_id] = thread
        monitoring_events[session_id] = stop_event

        try:
            thread.start()

        except Exception as error:
            monitoring_threads.pop(session_id, None)
            monitoring_events.pop(session_id, None)

            exam.monitoring_status = "failed"

            record_event(
                session_id,
                "monitoring_start_failure",
                str(error)
            )

            return False, "Unable to start face monitoring."

    return True, "Face monitoring started successfully."


def stop_monitoring(session_id):
    """Stop monitoring for the specified exam session."""

    with monitoring_lock:

        stop_event = monitoring_events.get(session_id)
        thread = monitoring_threads.get(session_id)

        if stop_event is None or thread is None:
            exam = db.session.get(ExamSession, session_id)

            if exam is None:
                return False, "Exam session not found."

            if exam.monitoring_status != "running":
                return False, "Monitoring is not running."

            return False, "Monitoring thread was not found."

        stop_event.set()

    # Wait briefly for the webcam to close.
    thread.join(timeout=5)

    if thread.is_alive():
        return False, "Monitoring is still stopping. Please wait."

    return True, "Face monitoring stopped successfully."


def monitor_exam(app, session_id, stop_event):
    """Capture webcam frames and detect faces."""

    camera = None
    previous_event = None
    monitoring_failed = False

    try:

        with app.app_context():

            exam = db.session.get(ExamSession, session_id)

            if exam is None or exam.status != "active":
                return

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades
                + "haarcascade_frontalface_default.xml"
            )

            if face_cascade.empty():

                monitoring_failed = True

                record_event(
                    session_id,
                    "detection_failure",
                    "Could not load the Haar Cascade model."
                )

                return

            camera = cv2.VideoCapture(0)

            if not camera.isOpened():

                monitoring_failed = True

                record_event(
                    session_id,
                    "camera_unavailable",
                    "Webcam unavailable or camera access was denied."
                )

                return

            print(
                f"Face monitoring started for session {session_id}"
            )

            while not stop_event.is_set():

                db.session.expire_all()

                exam = db.session.get(ExamSession, session_id)

                if exam is None or exam.status != "active":
                    break

                success, frame = camera.read()

                if not success:

                    monitoring_failed = True

                    record_event(
                        session_id,
                        "camera_read_failure",
                        "Could not read a webcam frame."
                    )

                    break

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                try:

                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )

                except cv2.error as error:

                    monitoring_failed = True

                    record_event(
                        session_id,
                        "detection_failure",
                        f"Face detection failed: {error}"
                    )

                    break

                face_count = len(faces)

                if face_count == 0:
                    event_type = "face_absent"
                    details = "No face detected."

                elif face_count == 1:
                    event_type = "face_present"
                    details = "One face detected."

                else:
                    event_type = "multiple_faces"
                    details = f"{face_count} faces detected."

                # Record only changes in face detection status.
                if event_type != previous_event:

                    record_event(
                        session_id,
                        event_type,
                        details
                    )

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

                cv2.imshow(
                    "ExamGuard Face Monitoring",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key in (ord("q"), ord("Q")):
                    stop_event.set()
                    break

    except Exception as error:

        monitoring_failed = True

        print(
            f"Monitoring error for session {session_id}: {error}"
        )

        with app.app_context():

            try:
                record_event(
                    session_id,
                    "monitoring_failure",
                    str(error)
                )

            except Exception:
                db.session.rollback()

    finally:

        # Always release the webcam.
        if camera is not None:
            camera.release()

        cv2.destroyAllWindows()

        with app.app_context():

            try:

                exam = db.session.get(
                    ExamSession,
                    session_id
                )

                if exam is not None:

                    if monitoring_failed:
                        exam.monitoring_status = "failed"
                    else:
                        exam.monitoring_status = "stopped"

                    if not monitoring_failed:
                        record_event(
                            session_id,
                            "monitoring_stopped",
                            "Face monitoring stopped."
                        )
                    else:
                        db.session.commit()

            except Exception:
                db.session.rollback()

        with monitoring_lock:
            monitoring_threads.pop(session_id, None)
            monitoring_events.pop(session_id, None)

        print(
            f"Face monitoring finished for session {session_id}"
        )