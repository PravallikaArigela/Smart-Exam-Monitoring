import os
import base64
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from app import db
from datetime import datetime, timezone
from app.face_monitor import (
    start_monitoring as start_face_monitoring,
    stop_monitoring as stop_face_monitoring
)
from app.models import Candidate, ExamSession, MonitoringEvent
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        photo_data = request.form.get("photo_data", "")

        if not name or not email or not password:
            flash("Please complete all fields.", "error")
            return redirect(url_for("main.register"))

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error"
            )
            return redirect(url_for("main.register"))

        if not photo_data:
            flash("Please capture your registration photo.", "error")
            return redirect(url_for("main.register"))

        existing = db.session.execute(
            select(Candidate).where(Candidate.email == email)
        ).scalar_one_or_none()

        if existing:
            flash("This email is already registered.", "error")
            return redirect(url_for("main.register"))

        # Validate and decode the browser-captured image.
        try:
            if not photo_data.startswith("data:image/jpeg;base64,"):
                raise ValueError("Invalid image format")

            encoded_image = photo_data.split(",", 1)[1]
            image_bytes = base64.b64decode(
                encoded_image,
                validate=True
            )

            # Prevent excessively large uploads.
            if len(image_bytes) > 5 * 1024 * 1024:
                raise ValueError("Image is too large")

        except (ValueError, base64.binascii.Error):
            flash("Invalid photo. Please capture it again.", "error")
            return redirect(url_for("main.register"))

        photo_folder = os.path.join(
            current_app.root_path,
            "static",
            "photos"
        )
        os.makedirs(photo_folder, exist_ok=True)

        photo_filename = f"{uuid.uuid4().hex}.jpg"
        photo_path = os.path.join(photo_folder, photo_filename)

        try:
            # Check that the uploaded bytes represent a readable image.
            import cv2
            import numpy as np

            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                flash("The captured photo is not a valid image.", "error")
                return redirect(url_for("main.register"))

            if image.shape[1] > 1920 or image.shape[0] > 1920:
                flash("Please use a smaller camera image.", "error")
                return redirect(url_for("main.register"))

            if not cv2.imwrite(photo_path, image):
                flash("Unable to save the registration photo.", "error")
                return redirect(url_for("main.register"))

            candidate = Candidate(
                name=name,
                email=email,
                photo_path=f"photos/{photo_filename}"
            )

            candidate.set_password(password)
            db.session.add(candidate)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            if os.path.exists(photo_path):
                os.remove(photo_path)

            flash("Unable to register this email.", "error")
            return redirect(url_for("main.register"))

        except Exception:
            db.session.rollback()

            if os.path.exists(photo_path):
                os.remove(photo_path)

            current_app.logger.exception(
                "Registration failed while saving candidate photo."
            )
            flash("Registration failed. Please try again.", "error")
            return redirect(url_for("main.register"))

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")




@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        candidate = db.session.execute(
            select(Candidate).where(Candidate.email == email)
        ).scalar_one_or_none()

        if candidate and candidate.check_password(password):

            session.clear()

            session["candidate_id"] = candidate.id

            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")



@main.route("/dashboard")
def dashboard():

    candidate_id = session.get("candidate_id")

    if candidate_id is None:
        flash("Please log in first.", "error")
        return redirect(url_for("main.login"))

    candidate = db.session.get(Candidate, candidate_id)

    if candidate is None:
        session.clear()
        flash("Please log in again.", "error")
        return redirect(url_for("main.login"))

    active_exam = ExamSession.query.filter_by(
        candidate_id=candidate_id,
        status="active"
    ).order_by(ExamSession.id.desc()).first()

    return render_template(
        "dashboard.html",
        candidate=candidate,
        active_exam=active_exam
    )

@main.route("/heartbeat", methods=["POST"])
def heartbeat():

    candidate_id = session.get("candidate_id")
    exam_session_id = session.get("exam_session_id")

    if candidate_id is None or exam_session_id is None:
        return {"success": False, "message": "No active session."}, 401

    exam = db.session.get(ExamSession, exam_session_id)

    if (
        exam is None
        or exam.candidate_id != candidate_id
        or exam.status != "active"
    ):
        return {"success": False, "message": "Exam is not active."}, 400

    now = datetime.now(timezone.utc)

    # Check whether the previous heartbeat is older than 60 seconds.
    if exam.last_heartbeat is not None:

        previous_heartbeat = exam.last_heartbeat

        # SQLite may return a datetime without timezone information.
        if previous_heartbeat.tzinfo is None:
            previous_heartbeat = previous_heartbeat.replace(
                tzinfo=timezone.utc
            )

        elapsed = (now - previous_heartbeat).total_seconds()

        if elapsed > 60:
            exam.status = "interrupted"
            exam.end_time = now

            db.session.add(
                MonitoringEvent(
                    session_id=exam.id,
                    event_type="session_interrupted",
                    event_time=now,
                    details="Heartbeat timeout: no browser activity received for more than 60 seconds."
                )
            )

            db.session.commit()
            
            if exam.monitoring_status == "running":
                stop_face_monitoring(exam.id)
                
            session.pop("exam_session_id", None)

            return {
                "success": False,
                "message": "Exam session interrupted due to heartbeat timeout."
            }, 409

    exam.last_heartbeat = now
    db.session.commit()

    return {"success": True}, 200



@main.route("/start_exam", methods=["POST"])
def start_exam():
    candidate_id = session.get("candidate_id")

    if candidate_id is None:
        flash("Please log in first.", "error")
        return redirect(url_for("main.login"))

    candidate = db.session.get(Candidate, candidate_id)

    if candidate is None:
        session.clear()
        flash("Please log in again.", "error")
        return redirect(url_for("main.login"))

    # Check whether this candidate already has an active exam.
    active_exam = db.session.execute(
        select(ExamSession).where(
            ExamSession.candidate_id == candidate_id,
            ExamSession.status == "active"
        ).order_by(ExamSession.id.desc())
    ).scalars().first()

    if active_exam:
        session["exam_session_id"] = active_exam.id
        flash("Your existing exam session is active.", "success")
        return redirect(url_for("main.dashboard"))

    # Create a new exam session.
    exam = ExamSession(
        candidate_id=candidate_id,
        status="active"
    )

    db.session.add(exam)
    db.session.flush()
    
    exam.last_heartbeat = datetime.now(timezone.utc)

    # Record that the exam session has started.
    event = MonitoringEvent(
        session_id=exam.id,
        event_type="session_started",
        details="Candidate started the examination."
    )

    db.session.add(event)
    db.session.commit()

    session["exam_session_id"] = exam.id

    flash("Exam session started successfully.", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/end_exam", methods=["POST"])
def end_exam():
    if "candidate_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("main.login"))

    candidate_id = session["candidate_id"]

    active_exam = ExamSession.query.filter_by(
        candidate_id=candidate_id,
        status="active"
    ).order_by(ExamSession.id.desc()).first()

    if not active_exam:
        session.pop("exam_session_id", None)
        flash("No active exam session was found.", "error")
        return redirect(url_for("main.dashboard"))


    if active_exam.monitoring_status == "running":
        success, message = stop_face_monitoring(active_exam.id)

        if not success:
            flash(message, "error")
            return redirect(url_for("main.dashboard"))

    active_exam.end_time = datetime.now(timezone.utc)
    active_exam.status = "completed"
    
    db.session.add( 
        MonitoringEvent( 
            session_id=active_exam.id, 
            event_type="session_ended", 
            event_time=datetime.now(timezone.utc), 
            details="Candidate ended the examination normally." 
        ) 
    )

    db.session.commit()

    session.pop("exam_session_id", None)

    flash("Exam ended successfully!", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/start_monitoring", methods=["POST"])
def start_monitoring():

    candidate_id = session.get("candidate_id")
    exam_session_id = session.get("exam_session_id")

    if candidate_id is None:
        flash("Please log in first.", "error")
        return redirect(url_for("main.login"))

    if exam_session_id is None:
        flash("Please start your exam first.", "error")
        return redirect(url_for("main.dashboard"))

    exam = db.session.get(ExamSession, exam_session_id)

    if (
        exam is None
        or exam.candidate_id != candidate_id
        or exam.status != "active"
    ):
        session.pop("exam_session_id", None)
        flash("No active exam found.", "error")
        return redirect(url_for("main.dashboard"))

    try:
        success, message = start_face_monitoring(exam.id)

        flash(message, "success" if success else "error")

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Unable to start face monitoring."
        )
        flash("Face monitoring could not be started.", "error")

    return redirect(url_for("main.dashboard"))

@main.route("/stop_monitoring_route", methods=["POST"])
def stop_monitoring_route():
    candidate_id = session.get("candidate_id")
    exam_session_id = session.get("exam_session_id")

    if not candidate_id or not exam_session_id:
        flash("No active exam session found.", "error")
        return redirect(url_for("main.dashboard"))

    exam = db.session.get(ExamSession, exam_session_id)

    if exam is None or exam.candidate_id != candidate_id:
        flash("Invalid exam session.", "error")
        return redirect(url_for("main.dashboard"))

    success, message = stop_face_monitoring(exam.id)
    flash(message, "success" if success else "error")

    return redirect(url_for("main.dashboard"))

@main.route("/logout", methods=["POST"])
def logout():
    candidate_id = session.get("candidate_id")
    exam_session_id = session.get("exam_session_id")

    if candidate_id and exam_session_id:
        exam = db.session.get(ExamSession, exam_session_id)

        if (
            exam is not None
            and exam.candidate_id == candidate_id
            and exam.monitoring_status == "running"
        ):
            success, message = stop_face_monitoring(exam.id)

            if not success:
                flash(message, "error")
                return redirect(url_for("main.dashboard"))

    session.clear()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("main.login"))