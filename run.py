
import time
import threading

from datetime import datetime, timezone, timedelta

from app import create_app, db
from app.models import Candidate, ExamSession, MonitoringEvent

app = create_app()


def check_inactive_sessions():

    while True:
        time.sleep(15)

        try:
            with app.app_context():

                now = datetime.now(timezone.utc)
                timeout_limit = timedelta(seconds=60)

                active_sessions = ExamSession.query.filter_by(
                    status="active"
                ).all()

                for exam in active_sessions:

                    last_activity = (
                        exam.last_heartbeat or exam.start_time
                    )

                    # SQLite may return timezone-naive datetimes.
                    if last_activity.tzinfo is None:
                        last_activity = last_activity.replace(
                            tzinfo=timezone.utc
                        )

                    elapsed = now - last_activity

                    if elapsed > timeout_limit:

                        exam.status = "interrupted"
                        exam.end_time = now

                        db.session.add(
                            MonitoringEvent(
                                session_id=exam.id,
                                event_type="session_interrupted",
                                event_time=now,
                                details=(
                                    "Heartbeat timeout: "
                                    "no browser activity received "
                                    "for more than 60 seconds."
                                )
                            )
                        )

                        print(
                            f"Session {exam.id} marked as interrupted."
                        )

                db.session.commit()

        except Exception as error:
            with app.app_context():
                db.session.rollback()

            print("Background checker error:", error)


def start_background_checker():

    checker_thread = threading.Thread(
        target=check_inactive_sessions,
        daemon=True
    )

    checker_thread.start()

    print("Background session timeout checker started.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":

    start_background_checker()

    app.run(debug=True, use_reloader=False)
