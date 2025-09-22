from flask import Flask, request, jsonify,session
from flask import Blueprint
from app.models import quizzes_collection,db

import google.generativeai as genai
import json,os

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# Dummy user (replace later with login session)


@quizzes_bp.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    user_email = session.get("user")
    topic= request.json.get("topic", "")
    
    questions = int(topic.get("questions", 5))

    if not topic:
        return jsonify({"error": "Topic is required"})

    prompt = f"""
    Generate {questions} multiple-choice questions on the topic "{topic}".
    Each question should have 4 options (A, B, C, D) and mention the correct answer clearly.
    Format output strictly as JSON with this structure:
    [
      {{"question": "string", "options": ["A", "B", "C", "D"]}}
    ]
    """

    try:
        response = model.generate_content(prompt)
        text_output = response.text

       
        quiz_data = json.loads(text_output)

        
        quizzes_collection.insert_one({
            "user": user_email,
            "topic": topic,
            "quiz": quiz_data
        })

        return jsonify({"quiz": quiz_data})
    except Exception as e:
        return jsonify({"error": str(e)})


@quizzes_bp.route("/get_quizzes", methods=["GET"])
def get_quizzes():
    user_email = session.get("user")
    records = list(quizzes_collection.find({"user":user_email}, {"_id": 0}))
    return jsonify(records)


@quizzes_bp.route("/clear_quizzes", methods=["POST"])
def clear_quizzes():
    user_email = session.get("user")
    quizzes_collection.delete_many({"user": user_email})
    return jsonify({"message": "All quizzes cleared!"})


# from flask import Blueprint, request, session, render_template, redirect, url_for
# from app.extensions import get_db

# quiz_bp = Blueprint('quiz', __name__)

# @quiz_bp.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     questions = [
#         {"id": 1, "question": "What is Python?", "options": ["Snake", "Programming Language", "Car", "Movie"]},
#         {"id": 2, "question": "What is Flask?", "options": ["Framework", "Animal", "Game", "Food"]},
#     ]
#     if request.method == 'POST':
#         user_email = session.get('user')
#         score = 0
#         for q in questions:
#             answer = request.form.get(f'question_{q["id"]}')
#             if q['id'] == 1 and answer == "Programming Language":
#                 score += 1
#             if q['id'] == 2 and answer == "Framework":
#                 score += 1
#         db = get_db()
#         db.execute(
#             "INSERT INTO quiz_scores (user_email, score) VALUES (?, ?)",
#             (user_email, score)
#         )
#         db.commit()
#         return redirect(url_for('quiz.quiz'))
#     return render_template('quiz.html', questions=questions)
