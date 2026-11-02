from unittest.mock import patch, MagicMock

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
        fake_camera = MagicMock()
        fake_camera.isOpened.return_value = True
        fake_camera.read.return_value = (False, None)

        with patch(
            "app.face_monitor.cv2.VideoCapture",
            return_value=fake_camera
        ):
            success, message = monitor_exam(exam.id)

        print("Monitoring result:", success, message)

        event = (
            db.session.query(MonitoringEvent)
            .filter_by(
                session_id=exam.id,
                event_type="camera_read_failure"
            )
            .order_by(MonitoringEvent.id.desc())
            .first()
        )

        if event:
            print("PASS: camera_read_failure event was saved.")
            print("Session ID:", event.session_id)
            print("Details:", event.details)
        else:
            print("FAIL: camera_read_failure event was not found.")