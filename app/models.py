from app.extensions import db


users_collection=db['users']
reminders_collection=db['reminders']
progress_collection=db['progress']
planner_collection = db["planner"]

quizzes_collection = db["quizzes"]
form_collection = db["form_collection"]
study_sessions_col = db["study_sessions"]
quiz_results_col = db["quiz_results"]
tasks_col = db["tasks"]

# from app.extensions import get_db
# import sqlite3

# class UserCollection:
#     @staticmethod
#     def find_one(query):
#         db = get_db()
#         cursor = db.execute(
#             "SELECT * FROM users WHERE email = ? AND password = ?", 
#             (query.get('email'), query.get('password'))
#         )
#         return cursor.fetchone()

#     @staticmethod
#     def insert_one(data):
#         db = get_db()
#         try:
#             db.execute(
#                 "INSERT INTO users (email, password) VALUES (?, ?)", 
#                 (data.get('email'), data.get('password'))
#             )
#             db.commit()
#         except sqlite3.IntegrityError:
#             return None

# users_collection = UserCollection()

