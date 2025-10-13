from flask import Flask, jsonify, render_template, redirect, url_for, session,Blueprint
from flask_pymongo import PyMongo
from app.models import users_collection,study_sessions_col,quiz_results_col,tasks_col
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date

dashboard_bp = Blueprint('dashboard', __name__,url_prefix='/dashboard')

# ---------------------------
# 🔗 MongoDB Configuration
# ---------------------------
# Replace with your MongoDB connection string:


# ------------------------------------------------------------
# AUTH ROUTES (for demo; you can replace with your real auth)
# ------------------------------------------------------------



# ------------------------------------------------------------
# DASHBOARD PAGE
# ------------------------------------------------------------
@dashboard_bp.route("/")
def home():
    return render_template('dashboard.html')

@dashboard_bp.route("/dashboard/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")


# ------------------------------------------------------------
# 📊 REAL DASHBOARD DATA API (MongoDB based)
# ------------------------------------------------------------
@dashboard_bp.route("/api/dashboard-data")
def dashboard_data():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = ObjectId(session["user_id"])
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())

    # --- STUDY TIME (Today & Yesterday) ---
    today_sessions = list(study_sessions_col.find({"user_id": user_id, "date": today.isoformat()}))
    study_time_today = sum(s.get("duration", 0) for s in today_sessions)

    yesterday_sessions = list(study_sessions_col.find({"user_id": user_id, "date": yesterday.isoformat()}))
    study_time_yesterday = sum(s.get("duration", 0) for s in yesterday_sessions)

    study_change = 0
    if study_time_yesterday > 0:
        study_change = round(((study_time_today - study_time_yesterday) / study_time_yesterday) * 100, 1)

    # --- STREAK CALCULATION ---
    streak = 0
    for i in range(7):
        d = today - timedelta(days=i)
        has_study = study_sessions_col.find_one({"user_id": user_id, "date": d.isoformat()})
        if has_study:
            streak += 1
        else:
            break

    # --- QUIZZES DONE (This week) ---
    quizzes = list(quiz_results_col.find({
        "user_id": user_id,
        "date": {"$gte": week_start.isoformat()}
    }))
    quizzes_done = len(quizzes)
    average_score = round(sum(q.get("score", 0) for q in quizzes) / quizzes_done, 2) if quizzes_done else 0

    # --- WEEKLY PROGRESS (Mon–Sun) ---
    weekly_progress = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        sessions = list(study_sessions_col.find({"user_id": user_id, "date": d.isoformat()}))
        total = sum(s.get("duration", 0) for s in sessions)
        weekly_progress.append(total)

    # --- UPCOMING TASKS ---
    tasks = list(tasks_col.find({
        "user_id": user_id,
        "date": {"$gte": today.isoformat()}
    }).sort("date", 1).limit(5))

    upcoming_tasks = [{
        "task": t["task"],
        "date": t["date"],
        "priority": t.get("priority", "medium")
    } for t in tasks]

    # --- COMPILE RESPONSE ---
    data = {
        "studyTimeToday": study_time_today,
        "studyChange": study_change,
        "studyStreak": streak,
        "quizzesDone": quizzes_done,
        "averageScore": average_score,
        "weeklyProgress": weekly_progress,
        "upcomingTasks": upcoming_tasks
    }

    return jsonify(data)





# ------------------------------------------------------------
# 🚀 RUN SERVER
# ------------------------------------------------------------
