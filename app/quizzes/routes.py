from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai
import os, json

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))




@quiz_bp.route("/")
def quiz_ui():
    return render_template("quiz.html")

@quiz_bp.route("/generate", methods=["POST"])
def generate_quiz():
    data = request.json
    topic = data.get("topic")
    num_questions = data.get("num_questions", 5)

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"""
    Generate {num_questions} multiple choice questions on the topic "{topic}".
    Return the output as a **valid JSON list**.
    Each question must follow this schema:
    [
      {{
        "question": "string",
        "options": ["A","B","C","D"],
        "correct_answer": "string"
      }}
    ]
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        response = model.generate_content(prompt)

        text_response = response.text.strip()

        # Try parsing as JSON
        try:
            quiz_data = json.loads(text_response)
        except json.JSONDecodeError:
            # If not valid JSON, wrap it into plain text
            return jsonify({"raw": text_response})

        return jsonify({"quiz": quiz_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
