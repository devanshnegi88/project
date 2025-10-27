from flask import Blueprint, jsonify, render_template
from app.models import users_collection, study_sessions_col, quizzes_collection, tasks_collection
from bson.objectid import ObjectId
from datetime import datetime, timedelta

planner_bp = Blueprint('planner', __name__, url_prefix='/planner')

@planner_bp.route('/')
def dashboard_page():
    return render_template('planner.html')

@planner_bp.route('/dashboard-data')
def dashboard_data():
    user_id = ObjectId("68ec90bf4699cec6b75a735e")
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    user = users_collection.find_one({'_id': user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # --- AI confidence ---
    study_sessions = list(study_sessions_col.find({'user_id': user_id}))
    total_topics = sum(s.get('total_topics', 0) for s in study_sessions)
    completed_topics = sum(s.get('topics_completed', 0) for s in study_sessions)
    ai_confidence = round((completed_topics / total_topics) * 100, 1) if total_topics else 0

    # --- Learning velocity ---
    weekly_hours = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        hours = sum(s.get('duration', 0) for s in study_sessions if s.get('date') == day.isoformat())
        weekly_hours.append(hours)
    learning_velocity = round(sum(weekly_hours)/7, 1)

    # --- Subjects overview ---
    subjects_dict = {}
    for s in study_sessions:
        subj = s.get('subject', 'Unknown')
        if subj not in subjects_dict:
            subjects_dict[subj] = {'name': subj, 'priority': 'Medium', 'topics_completed': 0, 'total_topics': 0, 'hours': 0}
        subjects_dict[subj]['topics_completed'] += s.get('topics_completed', 0)
        subjects_dict[subj]['total_topics'] += s.get('total_topics', 0)
        subjects_dict[subj]['hours'] += s.get('duration', 0)
    subjects = []
    for subj_data in subjects_dict.values():
        progress = round((subj_data['topics_completed']/subj_data['total_topics'])*100, 1) if subj_data['total_topics'] else 0
        subj_data['progress'] = progress
        subjects.append(subj_data)

    # --- Quizzes done and average score ---
    week_quizzes = list(quizzes_collection.find({
        'user_id': user_id,
        'date': {'$gte': week_start.isoformat()}
    }))
    quizzes_done = len(week_quizzes)
    average_score = round(sum(q['score'] for q in week_quizzes)/quizzes_done, 2) if quizzes_done else 0

    # --- Upcoming tasks (next 7 days) ---
    upcoming_tasks_cursor = tasks_collection.find({
        'user_id': user_id,
        'date': {'$gte': today.isoformat()}
    }).sort('date', 1)
    upcoming_tasks = []
    for t in upcoming_tasks_cursor:
        upcoming_tasks.append({
            'task': t.get('task'),
            'date': t.get('date'),
            'priority': t.get('priority', 'Medium')
        })

    return jsonify({
        "ai_confidence": ai_confidence,
        "learning_velocity": learning_velocity,
        "subjects": subjects,
        "quizzes_done": quizzes_done,
        "average_score": average_score,
        "upcoming_tasks": upcoming_tasks
    })
