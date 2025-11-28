from flask import Blueprint, request, jsonify, render_template, session
import google.generativeai as genai
import os, json
from datetime import datetime
from bson import ObjectId
from app.models import quizzes_collection
from app.activity_logger import log_activity

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@quiz_bp.route("/")
def quiz_ui():
    return render_template("quiz.html")

@quiz_bp.route("/generate", methods=["POST"])
def generate_quiz():
    data = request.json
    subject = data.get("subject")
    topic = data.get("topic")
    num_questions = data.get("num_questions", 5)

    if not topic or not subject:
        return jsonify({"error": "Subject and topic are required"}), 400

    prompt = f"""
    Generate {num_questions} multiple choice questions about {topic} in {subject}.
    Return the output as a valid JSON list.
    Each question must follow this schema:
    [
      {{
        "question": "string",
        "options": ["A","B","C","D"],
        "correct_answer": "string"
      }}
    ]
    Make sure the questions are challenging but appropriate for the subject level.
    Include clear and concise questions with 4 options each.
    One of the options must be the correct answer.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        response = model.generate_content(prompt)
        text_response = response.text.strip()

        # Try parsing as JSON
        try:
            quiz_data = json.loads(text_response)
            
            # Store quiz in database
            new_quiz = {
                "subject": subject,
                "topic": topic,
                "questions": quiz_data,
                "created_at": datetime.now()
            }
            quizzes_collection.insert_one(new_quiz)
            
            return jsonify(quiz_data)
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to clean up the response
            clean_response = text_response.replace("```json", "").replace("```", "").strip()
            try:
                quiz_data = json.loads(clean_response)
                
                # Store quiz in database
                new_quiz = {
                    "subject": subject,
                    "topic": topic,
                    "questions": quiz_data,
                    "created_at": datetime.now()
                }
                quizzes_collection.insert_one(new_quiz)
                
                return jsonify(quiz_data)
            except:
                return jsonify({"error": "Failed to generate valid quiz questions"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route("/history")
def quiz_history():
    quizzes = list(quizzes_collection.find({}, {"_id": 0}))
    return jsonify(quizzes)


@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    # Get user_id from session (try both formats)
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    elif 'user' in session and isinstance(session['user'], dict) and session['user'].get('id'):
        user_id = session['user'].get('id')
    
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    subject = data.get('subject', 'General')
    score = data.get('score', 0)
    total = data.get('total', 1)
    correct = data.get('correct', 0)
    time_taken = data.get('time_taken', 0)

    # ✅ Save in DB with required fields
    today = datetime.now().date().isoformat()
    quizzes_collection.insert_one({
        "user_id": str(user_id),  # Store as string for consistency
        "subject": subject,
        "score": float(score),  # Percentage (0-100)
        "raw_score": correct,
        "total": total,
        "time_taken_seconds": time_taken,
        "date": today,
        "created_at": datetime.now()
    })

    # ✅ Auto log activity
    try:
        from app.activity_logger import log_activity
        log_activity(str(user_id), "quiz_completed", {"subject": subject, "score": score})
    except:
        pass

    return jsonify({"success": True, "message": "Quiz submitted successfully"})

# @quiz_bp.route('/submit', methods=['POST'])
# def submit_quiz():
#     """Receive quiz results from frontend and store score with user info."""
#     data = request.get_json() or {}
#     score = data.get('score')  # numeric raw score (e.g., 4)
#     total = data.get('total')  # total questions (e.g., 5)
#     percentage = data.get('percentage')  # percentage (0-100)
#     time_taken = data.get('time_taken')  # seconds
#     subject = data.get('subject')
#     topic = data.get('topic')

#     # Resolve user id from session
#     user_id = None
#     if 'user_id' in session:
#         user_id = session['user_id']
#     elif 'user' in session and isinstance(session['user'], dict) and session['user'].get('id'):
#         user_id = session['user'].get('id')

#     if not user_id:
#         return jsonify({'error': 'User not logged in'}), 401

#     try:
#         # Store a quiz-result document
#         quiz_result = {
#             'user_id': str(user_id),
#             'score': float(percentage) if percentage is not None else (float(score) / float(total) * 100 if score is not None and total else 0),
#             'raw_score': score,
#             'total': total,
#             'percentage': float(percentage) if percentage is not None else None,
#             'time_taken_seconds': time_taken,
#             'subject': subject,
#             'topic': topic,
#             'date': datetime.now().date().isoformat(),
#             'created_at': datetime.now()
#         }
#         quizzes_collection.insert_one(quiz_result)
#         return jsonify({'status': 'success', 'inserted': True}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
