import json
from flask import Blueprint, request, jsonify, render_template
from app.models import planner_collection
import google.generativeai as genai

from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

planner_bp = Blueprint("planner", __name__, url_prefix='/planner')

@planner_bp.route("/planner")
def planner():
    return render_template('planner.html')

# Save manual schedule to MongoDB
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

# Load manual schedule from MongoDB
@planner_bp.route("/get_manual_schedule", methods=["GET"])
def get_manual_schedule():
    schedule = planner_collection.find_one({"_id": "manual_schedule"})
    if not schedule:
        return jsonify({}), 200
    return jsonify(schedule.get("schedule", {})), 200

# Clear manual schedule from MongoDB
@planner_bp.route("/clear_manual_schedule", methods=["POST"])
def clear_manual_schedule():
    planner_collection.update_one(
        {"_id": "manual_schedule"},
        {"$set": {"schedule": {}}}
    )
    return jsonify({"message": "Manual schedule cleared!"}), 200

# Generate AI schedule using Gemini and save to MongoDB
@planner_bp.route("/generate_ai_schedule", methods=["POST"])
def generate_ai_schedule():
    data = request.json
    subjects = data.get("subjects", [])
    hours = data.get("hours", 1)

    if not subjects or hours <= 0:
        return jsonify({"error": "Invalid subjects or hours"}), 400

    prompt = f"""
    Create a weekly study schedule in plain text for a student who wants to study the following subjects: {', '.join(subjects)}.
    The student has {hours} hours available per day.
    Distribute study tasks intelligently from Monday to Sunday.
    Output format:
    Monday: task1, task2, ...
    Tuesday: ...
    Wednesday: ...
    Thursday: ...
    Friday: ...
    Saturday: ...
    Sunday: ...
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        text_output = response.text

        # Save the text schedule to MongoDB (optional)
        planner_collection.update_one(
            {"_id": "ai_schedule"},
            {"$set": {"schedule_text": text_output}},
            upsert=True
        )

        return jsonify({"schedule": text_output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500