from flask import jsonify, Blueprint, render_template
from bson import ObjectId
from datetime import datetime, timedelta
from app.models import users_collection, tasks_collection, quizzes_collection

dashboard_bp = Blueprint('dashboard', __name__,url_prefix='/api')
@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard-data')
def dashboard_data():
    # Use your actual user ObjectId
    user_id = ObjectId("68ec90bf4699cec6b75a735e")

    # Fetch user document
    user = users_collection.find_one({'_id': user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Dates as ISO strings
    today = datetime.now().date()
    today_str = today.isoformat()
    yesterday_str = (today - timedelta(days=1)).isoformat()

    # Study time today
    study_time_today = user.get('study_time', {}).get(today_str, 0)

    # Change from yesterday
    study_yesterday = user.get('study_time', {}).get(yesterday_str, 0)
    study_change = ((study_time_today - study_yesterday) / study_yesterday * 100) if study_yesterday else 100

    # Study streak
    study_streak = user.get('study_streak', 0)

    # Quizzes done this week
    week_start_str = (today - timedelta(days=today.weekday())).isoformat()
    quizzes_done = quizzes_collection.count_documents({
    'user_id': str(user_id),
    'date': {'$gte': week_start_str}
})
    

    # Average score
    quiz_scores_cursor = quizzes_collection.find({'user_id': str(user_id)}, {'score': 1})
    quiz_scores = [q.get('score', 0) for q in quiz_scores_cursor]
    average_score = round(sum(quiz_scores) / len(quiz_scores), 2) if quiz_scores else 0

    # Weekly progress (last 7 days)
    weekly_progress = []
    for i in range(7):
        day_str = (today - timedelta(days=6-i)).isoformat()
        weekly_progress.append(user.get('study_time', {}).get(day_str, 0))

    # Upcoming tasks (next 5)
    upcoming_tasks_cursor = tasks_collection.find({
        'user_id': str(user_id),
        'date': {'$gte': today_str}
    }).sort('date', 1).limit(5)

    upcoming_tasks = []
    for t in upcoming_tasks_cursor:
        upcoming_tasks.append({
            'task': t.get('task_name', 'No Name'),
            'date': t.get('date', today_str),
            'priority': t.get('priority', 'low')
        })

    # Return JSON
    return jsonify({
        'studyTimeToday': study_time_today,
        'studyChange': round(study_change, 2),
        'studyStreak': study_streak,
        'quizzesDone': quizzes_done,
        'averageScore': average_score,
        'weeklyProgress': weekly_progress,
        'upcomingTasks': upcoming_tasks
    })
