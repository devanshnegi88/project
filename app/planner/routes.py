# from .import planner_bp
import json

from flask import Flask,Blueprint, request, jsonify, render_template,session,render_template, redirect, url_for
from app.models import planner_collection
import google.generativeai as genai

planner_bp=Blueprint("planner",__name__, url_prefix='/planner')

@planner_bp.route("/planner")
def planner():
    
    return render_template('planner.html')


@planner_bp.route("/save_manual_schedule", methods=["POST"])
def save_manual_schedule():
    data = request.json
    schedule = data.get("schedule", {})
    planner_collection.update_one(
        {"_id": "manual_schedule"},
        {"$set": {"schedule": schedule}},
        upsert=True
    )
    return jsonify({"message": "Manual schedule saved successfully!"}), 200


@planner_bp.route("/get_manual_schedule", methods=["GET"])
def get_manual_schedule():
    schedule= planner_collection.find_one({"_id": "manual_schedule"})
    if not schedule:
        return jsonify({}), 200
    return jsonify(schedule.get("schedule", {})), 200


@planner_bp.route("/clear_manual_schedule", methods=["POST"])
def clear_manual_schedule():
    planner_collection.update_one(
        {"_id": "manual_schedule"},
        {"$set": {"schedule": {}}}
    )
    return jsonify({"message": "Manual schedule cleared!"}), 200

@planner_bp.route("/generate_ai_schedule", methods=["POST"])
def generate_ai_schedule():
    data = request.json
    subjects = data.get("subjects", [])
    hours = data.get("hours", 1)

    if not subjects or hours <= 0:
        return jsonify({"error": "Invalid subjects or hours"}), 400

    prompt = f"""
    Create a weekly study schedule in JSON format for a student who wants to study the following subjects: {', '.join(subjects)}.
    The student has {hours} hours available per day.
    Distribute study tasks intelligently from Monday to Sunday.
    Output format:
    {{
      "Monday": ["task1", "task2", ...],
      "Tuesday": [...],
      "Wednesday": [...],
      "Thursday": [...],
      "Friday": [...],
      "Saturday": [...],
      "Sunday": [...]
    }}
    """

    try:
        model=genai.GenrativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text_output = response.text

        schedule = json.loads(text_output)

        # Optionally, save generated schedule
        planner_collection.update_one(
            {"_id": "ai_schedule"},
            {"$set": {"schedule": schedule}},
            upsert=True
        )

        return jsonify(schedule), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# from flask import Blueprint, request, session, render_template, redirect, url_for
# from app.extensions import get_db

# planner_bp = Blueprint('planner', __name__)

# @planner_bp.route('/planner', methods=['GET', 'POST'])
# def planner():
#     db = get_db()
#     if request.method == 'POST':
#         schedule = request.form.get('schedule')
#         user_email = session.get('user')
#         if user_email:
#             db.execute(
#                 "INSERT INTO planner (user_email, schedule) VALUES (?, ?)",
#                 (user_email, schedule)
#             )
#             db.commit()
#             return redirect(url_for('planner.planner'))
#     user_email = session.get('user')
#     schedules = []
#     if user_email:
#         cursor = db.execute(
#             "SELECT schedule FROM planner WHERE user_email = ?", (user_email,)
#         )
#         schedules = cursor.fetchall()
#     return render_template('planner.html', schedules=schedules)
