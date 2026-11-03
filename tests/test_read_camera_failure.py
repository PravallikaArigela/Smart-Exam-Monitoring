from unittest.mock import patch, MagicMock
import threading

import pytest

from app import create_app, db
from app.models import ExamSession, MonitoringEvent
from app.face_monitor import monitor_exam


def test_camera_read_failure_event():
    app = create_app()

    with app.app_context():
        exam = (
            db.session.query(ExamSession)
            .filter_by(status="active")
            .order_by(ExamSession.id.desc())
            .first()
        )

        if exam is None:
            pytest.skip("No active exam session found.")

        fake_camera = MagicMock()
        fake_camera.isOpened.return_value = True
        fake_camera.read.return_value = (False, None)

        stop_event = threading.Event()

        with patch(
            "app.face_monitor.cv2.VideoCapture",
            return_value=fake_camera
        ):
            monitor_exam(app, exam.id, stop_event)

        event = (
            db.session.query(MonitoringEvent)
            .filter_by(
                session_id=exam.id,
                event_type="camera_read_failure"
            )
            .order_by(MonitoringEvent.id.desc())
            .first()
        )

        assert event is not None
        assert event.session_id == exam.id