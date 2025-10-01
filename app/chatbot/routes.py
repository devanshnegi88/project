from flask import Blueprint, request, jsonify, render_template
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # load variables from .env

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# ✅ Configure Gemini API securely (do not expose in frontend)
GEMINI_API_KEY = "AIzaSyBLZZY8iaMu6Hkz9SEknSAF7qrCc4kdnAE"
genai.configure(api_key=GEMINI_API_KEY)


@chatbot_bp.route("/")
def chatbot_ui():
    """Serve the chatbot frontend page"""
    return render_template("chatbot.html")


@chatbot_bp.route("/chatbot", methods=["POST"])
def chatbot_api():
    """Handle chatbot API requests"""
    try:
        data = request.json
        user_message = data.get("message", "")
        

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Use Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(user_message)

        reply = response.text if response.text else "⚠️ No response from AI"
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
