import threading
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest

from app import create_app, db
from app.models import ExamSession, MonitoringEvent
from app.face_monitor import monitor_exam


def test_detection_failure_event():
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
        fake_camera.read.return_value = (
            True,
            np.zeros((100, 100, 3), dtype="uint8")
        )

        stop_event = threading.Event()

        with patch(
            "app.face_monitor.cv2.VideoCapture",
            return_value=fake_camera
        ), patch(
            "app.face_monitor.cv2.CascadeClassifier.detectMultiScale",
            side_effect=cv2.error("Simulated detection failure")
        ):
            monitor_exam(app, exam.id, stop_event)

        event = (
            db.session.query(MonitoringEvent)
            .filter_by(
                session_id=exam.id,
                event_type="detection_failure"
            )
            .order_by(MonitoringEvent.id.desc())
            .first()
        )

        assert event is not None
        assert event.session_id == exam.id