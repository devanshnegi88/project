from flask import Flask, jsonify, session, redirect, url_for,Blueprint, render_template, request
from app.models import users_collection
from flask_pymongo import PyMongo
from datetime import timedelta
dashboard_bp = Blueprint("dashboard", __name__, url_prefix='/dashboard')



@dashboard_bp.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")   

@dashboard_bp.route("/api/user_progress")
def user_progress():
    email = session.get("user")
    if not email:
        return jsonify({})  # return empty object if not logged in

    user = users_collection.find_one({"email": email}, {"_id": 0})
    if not user:
        # defaults for new users
        user = {
            "studyMinutes": 0,
            "topicsCompleted": 0,
            "quizPerformance": 0,
            "focusScore": 0,
            "studyHistory": [0,0,0,0,0,0,0],
            "quizHistory": [0,0,0,0,0,0,0]
        }
    return jsonify(user)




