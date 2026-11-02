from unittest.mock import patch

from app import create_app, db
from app.models import ExamSession, MonitoringEvent
from app.face_monitor import monitor_exam

app = create_app()

with app.app_context():
    exam = (
        db.session.query(ExamSession)
        .filter_by(status="active")
        .order_by(ExamSession.id.desc())
        .first()
    )

    if exam is None:
        print("No active exam session found. Start an exam first.")
    else:
        try:
            with patch(
                "app.face_monitor.cv2.CascadeClassifier.detectMultiScale",
                side_effect=__import__("cv2").error(
                    "Simulated detection failure"
                )
            ):
                with patch(
                    "app.face_monitor.cv2.VideoCapture"
                ) as mock_camera:
                    camera = mock_camera.return_value
                    camera.isOpened.return_value = True
                    camera.read.return_value = (
                        True,
                        __import__("numpy").zeros(
                            (100, 100, 3), dtype="uint8"
                        )
                    )

                    success, message = monitor_exam(exam.id)

            print("Monitoring result:", success, message)

        except Exception as error:
            print("Test execution error:", error)

        event = (
            db.session.query(MonitoringEvent)
            .filter_by(
                session_id=exam.id,
                event_type="detection_failure"
            )
            .order_by(MonitoringEvent.id.desc())
            .first()
        )

        if event:
            print("PASS: detection_failure event was saved.")
            print("Session ID:", event.session_id)
            print("Details:", event.details)
        else:
            print("FAIL: detection_failure event was not found.")