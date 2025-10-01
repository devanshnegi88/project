from flask import Blueprint, request, session, render_template, jsonify,redirect, url_for
from bson.objectid import ObjectId
from app.models import reminders_collection

reminders_bp = Blueprint("reminders", __name__, url_prefix="/reminders")

# Render the reminders page
@reminders_bp.route("/reminders", methods=["GET"])
def reminders_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    # Fetch reminders for the user
    reminders = list(reminders_collection.find({"user": session["user"]}))
    
    # Convert ObjectId to string for frontend usage
    for r in reminders:
        r["_id"] = str(r["_id"])

    # Pass reminders to the template
    return render_template("reminder.html", reminders=reminders)


# API endpoint for frontend JS to fetch reminders (optional)
@reminders_bp.route("/api", methods=["GET"])
def get_reminders_api():
    if "user" not in session:
        return jsonify([])
    reminders = list(reminders_collection.find({"user": session["user"]}))
    for r in reminders:
        r["_id"] = str(r["_id"])
    return jsonify(reminders)


# Add a reminder
@reminders_bp.route("/add", methods=["POST"])
def add_reminder():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    reminders_collection.insert_one({
        "user": session["user"],
        "title": data["title"],
        "time": data["time"]
    })
    return jsonify({"status": "success"}), 201


# Delete a reminder
@reminders_bp.route("/<id>", methods=["DELETE"])
def delete_reminder(id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    reminders_collection.delete_one({"_id": ObjectId(id), "user": session["user"]})
    return jsonify({"status": "deleted"})
