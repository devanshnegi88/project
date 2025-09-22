from flask import Flask, request, jsonify,Blueprint
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # ✅ allows frontend (HTML file opened in browser) to call backend

# ✅ Folder to temporarily store uploaded videos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


notes_sumariser_bp = Blueprint("notes_sumariser", __name__, url_prefix='/notes_sumariser')


# --- Mock AI Notes Generator ---
def generate_lecture_notes(source: str, mode: str = "video"):
    """
    Fake notes generator function.
    Replace this with real Gemini/OpenAI summarisation logic.
    """
    if mode == "video":
        return f"📝 Notes generated from uploaded video: {source}\n\n- Point 1\n- Point 2\n- Point 3"
    else:
        return f"📝 Notes generated from YouTube link: {source}\n\n- Summary point A\n- Summary point B\n- Summary point C"


# --- Summarisation Route ---
@notes_sumariser_bp.route("/sumariser", methods=["POST"])
def summarise():
    try:
        # Case 1: YouTube link (JSON)
        if request.is_json:
            data = request.get_json()
            youtube_url = data.get("youtube_url")
            if not youtube_url:
                return jsonify({"error": "No YouTube URL provided"}), 400

            notes = generate_lecture_notes(youtube_url, mode="youtube")
            return jsonify({"notes": notes})

        # Case 2: Video Upload (FormData)
        if "video" in request.files:
            video_file = request.files["video"]
            if video_file.filename == "":
                return jsonify({"error": "No video file selected"}), 400

            save_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
            video_file.save(save_path)

            notes = generate_lecture_notes(video_file.filename, mode="video")
            return jsonify({"notes": notes})

        return jsonify({"error": "Invalid request. Provide either YouTube link or video file."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500



