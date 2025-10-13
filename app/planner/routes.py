# backend_ai.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

# ----------------- Setup ----------------- #
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for frontend

# Connect to MongoDB (replace with your URI)
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_study_planner"]
subjects_col = db["subjects"]

# ----------------- Helper ----------------- #
def serialize_subject(subj):
    return {
        "id": str(subj["_id"]),
        "name": subj.get("name", ""),
        "chapters": subj.get("chapters", 0),
        "progress": subj.get("progress", 0),
        "priority": subj.get("priority", "High"),
        "color": subj.get("color", "#4F46E5")
    }

def priority_weight(priority):
    if priority.lower() == "high":
        return 1.5
    elif priority.lower() == "medium":
        return 1.0
    else:
        return 0.7

# ----------------- Dashboard Endpoint ----------------- #
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        subjects = list(subjects_col.find())
        if not subjects:
            return jsonify({
                "aiConfidence": 0,
                "learningVelocity": 0,
                "learningChange": 0,
                "subjects": []
            })

        # ---- Weighted AI Confidence ---- #
        total_weighted_progress = 0
        total_weight = 0
        for subj in subjects:
            weight = priority_weight(subj.get("priority", "High"))
            total_weighted_progress += subj.get("progress", 0) * weight
            total_weight += weight
        ai_confidence = round(total_weighted_progress / total_weight) if total_weight > 0 else 0

        # ---- Learning Velocity Prediction ---- #
        # Velocity = avg progress per chapter, scaled by priority
        velocity_sum = 0
        for subj in subjects:
            chapters = max(subj.get("chapters", 1), 1)
            progress = subj.get("progress", 0)
            weight = priority_weight(subj.get("priority", "High"))
            velocity_sum += (progress / chapters) * weight * 5  # scaled 0-5
        learning_velocity = round(velocity_sum / len(subjects), 1)

        # ---- Learning Change ---- #
        if not hasattr(app, "last_ai_confidence"):
            app.last_ai_confidence = ai_confidence
        learning_change = ai_confidence - app.last_ai_confidence
        app.last_ai_confidence = ai_confidence

        return jsonify({
            "aiConfidence": ai_confidence,
            "learningVelocity": learning_velocity,
            "learningChange": learning_change,
            "subjects": [serialize_subject(s) for s in subjects]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- Add Subject ----------------- #
@app.route("/api/subjects/add", methods=["POST"])
def add_subject():
    data = request.json
    name = data.get("name")
    chapters = int(data.get("chapters", 0))
    priority = data.get("priority", "High")
    if not name or chapters <= 0:
        return jsonify({"error": "Invalid data"}), 400
    new_subject = {
        "name": name,
        "chapters": chapters,
        "progress": 0,
        "priority": priority,
        "color": "#4F46E5"
    }
    result = subjects_col.insert_one(new_subject)
    return jsonify({"success": True, "id": str(result.inserted_id)})

# ----------------- Edit Subject ----------------- #
@app.route("/api/subjects/edit/<id>", methods=["PUT"])
def edit_subject(id):
    data = request.json
    name = data.get("name")
    chapters = int(data.get("chapters", 0))
    priority = data.get("priority", "High")
    if not name or chapters <= 0:
        return jsonify({"error": "Invalid data"}), 400
    subjects_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"name": name, "chapters": chapters, "priority": priority}}
    )
    return jsonify({"success": True})

# ----------------- Delete Subject ----------------- #
@app.route("/api/subjects/delete/<id>", methods=["DELETE"])
def delete_subject(id):
    subjects_col.delete_one({"_id": ObjectId(id)})
    return jsonify({"success": True})

# ----------------- Run App ----------------- #

    app.run(debug=True)