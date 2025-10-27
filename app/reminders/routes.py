from flask import Blueprint, request, jsonify,render_template,session
from bson import ObjectId
from datetime import datetime,timezone
from app.models import reminders_collection

import os

reminders_bp = Blueprint("reminders", __name__, url_prefix="/reminders")

# connect to MongoDB Atlas
@reminders_bp.route("/")
def home():
    return render_template("reminder.html")

# 🕒 Ensure TTL index exists
# This deletes documents automatically after their 'time' passes
reminders_collection.create_index("time", expireAfterSeconds=0)

# ✅ Fetch active reminders
@reminders_bp.route("/api", methods=["GET"])
def get_reminders():
    now = datetime.utcnow()
    reminders = list(reminders_collection.find({"time": {"$gt": now}}))
    for r in reminders:
        r["_id"] = str(r["_id"])
    return jsonify(reminders)

# ✅ Add a new reminder
@reminders_bp.route("/add", methods=["POST"])
def add_reminder():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json

    # Convert frontend local time to UTC before saving
    local_time = datetime.fromisoformat(data["time"])
    utc_time = local_time.astimezone(timezone.utc)

    result = reminders_collection.insert_one({
        "user": session["user"],
        "title": data["title"],
        "time": utc_time
    })

    return jsonify({
        "status": "success",
        "_id": str(result.inserted_id),
        "title": data["title"],
        "time": data["time"]  # send back original local time for UI
    }), 201

# ✅ Delete a reminder manually
@reminders_bp.route("/<reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    reminders_collection.delete_one({"_id": ObjectId(reminder_id)})
    return jsonify({"message": "Deleted"})
