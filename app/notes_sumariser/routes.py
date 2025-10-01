from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv



load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

notes_bp = Blueprint("notes_sumariser", __name__, url_prefix="/notes_sumariser")

@notes_bp.route("/sumariser")
def sumariser_ui():
    return render_template("notes_summariser.html")

@notes_bp.route("/summarise_local", methods=["POST"])
def summarise_local():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    video = request.files["video"]
    filename = secure_filename(video.filename)
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    video.save(temp_path)

    # TODO: Extract audio & transcribe (use whisper or similar)
    # For demo, we'll just fake transcript
    transcript = "This is a fake transcript from the uploaded video."

    # Summarise using Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"Summarise these notes: {transcript}")
    summary = response.text if response.text else "No summary generated."
    os.remove(temp_path)
    return jsonify({"summary": summary})

@notes_bp.route("/summarise_youtube", methods=["POST"])
def summarise_youtube():
    data = request.get_json()
    yt_url = data.get("url")
    if not yt_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    # TODO: Download & transcribe YouTube video (use pytube + whisper)
    # For demo, we'll just fake transcript
    transcript = f"Transcript from YouTube video at {yt_url}"

    # Summarise using Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"Summarise these notes: {transcript}")
    summary = response.text if response.text else "No summary generated."
    return jsonify({"summary": summary})