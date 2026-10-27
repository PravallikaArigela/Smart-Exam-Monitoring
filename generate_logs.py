from datetime import timedelta, timezone
from random import choice, randint

from faker import Faker

from app import create_app, db
from app.models import Candidate, ExamSession, MonitoringEvent

fake = Faker()

# Create the Flask application
app = create_app()

# These records are synthetic test data, not real exam activity.
EVENT_TYPES = [
    "face_detected",
    "face_missing",
    "multiple_faces",
    "looking_away",
    "session_started",
    "session_ended",
]


def generate_logs():
    with app.app_context():

        # Use existing registered candidates.
        candidates = Candidate.query.all()

        if not candidates:
            print("No candidates found.")
            print("Register a test candidate before running this script.")
            return

        # Generate sessions and events for existing candidates.
        for candidate in candidates:
            for _ in range(randint(1, 2)):

                start_time = fake.date_time_between(
                    start_date="-7d",
                    end_date="now",
                    tzinfo=timezone.utc,
                )

                session = ExamSession(
                    candidate_id=candidate.id,
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=randint(15, 60)),
                    status="completed",
                )

                db.session.add(session)
                db.session.flush()  # Assigns the session ID.

                # Add a session-started event.
                db.session.add(
                    MonitoringEvent(
                        session_id=session.id,
                        event_type="session_started",
                        event_time=start_time,
                        details="[SYNTHETIC TEST DATA] Exam session started.",
                    )
                )

                # Add random monitoring events during the session.
                event_count = randint(3, 6)

                for _ in range(event_count):
                    event_type = choice(EVENT_TYPES[:4])

                    event_time = start_time + timedelta(
                        minutes=randint(1, 50)
                    )

                    db.session.add(
                        MonitoringEvent(
                            session_id=session.id,
                            event_type=event_type,
                            event_time=event_time,
                            details=(
                                "[SYNTHETIC TEST DATA] "
                                + fake.sentence()
                            ),
                        )
                    )

                # Add a session-ended event.
                db.session.add(
                    MonitoringEvent(
                        session_id=session.id,
                        event_type="session_ended",
                        event_time=session.end_time,
                        details="[SYNTHETIC TEST DATA] Exam session ended.",
                    )
                )

        db.session.commit()

        print("Synthetic data generated successfully!")
        print("Total candidates:", Candidate.query.count())
        print("Total exam sessions:", ExamSession.query.count())
        print("Total monitoring events:", MonitoringEvent.query.count())


if __name__ == "__main__":
    try:
        generate_logs()
    except Exception:
        with app.app_context():
            db.session.rollback()
        raise

