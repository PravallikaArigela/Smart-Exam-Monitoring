from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False
    )

    photo_path = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )
        
        
class ExamSession(db.Model):
    __tablename__ = "exam_sessions"

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidates.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    end_time = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )

    # One candidate can have multiple examination sessions
    candidate = db.relationship(
        "Candidate",
        backref=db.backref("exam_sessions", lazy=True)
    )

    # One examination session can have multiple monitoring events
    monitoring_events = db.relationship(
        "MonitoringEvent",
        backref="exam_session",
        lazy=True,
        cascade="all, delete-orphan"
    )


class MonitoringEvent(db.Model):
    __tablename__ = "monitoring_events"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_sessions.id"),
        nullable=False
    )

    event_type = db.Column(
        db.String(50),
        nullable=False
    )

    event_time = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    details = db.Column(db.Text, nullable=True)

