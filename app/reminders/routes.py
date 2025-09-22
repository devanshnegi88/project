from  flask import Flask,Blueprint,session,url_for,request,redirect,render_template,session

from app.models import reminders_collection
# from app.extensions import send_email
reminders_bp=Blueprint("reminders",__name__, url_prefix='/reminders')



@reminders_bp.route("/reminders")
def reminder():
    
    return render_template('reminder.html')
@reminders_bp.route('/add',methods=["POST"])
def add_reminder():
    if "user" not in session:
        return redirect(url_for('auth.login'))
    
    reminder=request.form.get("reminder")
    date=request.form.get("date")
    if reminder:
        # ~

        reminders=list(reminders_collection.find_one({'user':session['user'],'reminder':reminder,'date':date}))

    return render_template('reminders.html',reminders=reminders)    

@reminders_bp.route('/delete',methods=['GET','POST'])
def delete_reminder(reminder):
    if "user" not in session:
        return redirect(url_for('auth.login'))
    
    if reminder:
       reminders_collection.delete_one({'user':session['user'],'reminder':reminder})
    return redirect(url_for('reminders.view_reminder'))  


@reminders_bp.route('/view',methods=['GET'])
def view_reminder(reminder,date):
    if "user" not in session:
        return redirect(url_for('auth.login'))
    
    if reminder:
        reminders=list(reminders_collection.find_one({'reminder':reminder,'date':date}))
    return render_template('reminder.html',reminders=reminders) 
# 
# from flask import Blueprint, request, session, render_template, redirect, url_for
# from app.extensions import get_db

# reminders_bp = Blueprint('reminders', __name__)

# @reminders_bp.route('/reminders', methods=['GET', 'POST'])
# def reminders():
#     db = get_db()
#     if request.method == 'POST':
#         reminder = request.form.get('reminder')
#         user_email = session.get('user')
#         if user_email:
#             db.execute(
#                 "INSERT INTO reminders (user_email, reminder) VALUES (?, ?)",
#                 (user_email, reminder)
#             )
#             db.commit()
#             return redirect(url_for('reminders.reminders'))
#     user_email = session.get('user')
#     reminders = []
#     if user_email:
#         cursor = db.execute(
#             "SELECT reminder FROM reminders WHERE user_email = ?", (user_email,)
#         )
#         reminders = cursor.fetchall()
#     return render_template('reminders.html', reminders=reminders)
   