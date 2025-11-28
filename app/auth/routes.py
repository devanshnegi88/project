# from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from bson import ObjectId
# from flask_dance.contrib.google import google
# from app.models import users_collection
# import secrets
# from datetime import datetime, timedelta

# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# # Login page
# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')

#         user = users_collection.find_one({'email': email, 'password': password})
#         if user:
#             session['user'] = email
#             return redirect(url_for('dashboard.dashboard'))  # redirect to dashboard
#         else:
#             flash("Invalid credentials. Please try again.", "error")
#             return render_template("login.html")

#     return render_template("login.html")

# # Signup page
# @auth_bp.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         confirm = request.form.get('confirm_password')  # HTML input name="confirm_password"

#         if password != confirm:
#             flash("Passwords do not match.", "error")
#             return render_template("signup.html")

#         existing_user = users_collection.find_one({'email': email})
#         if existing_user:
#             flash("User already exists. Please login.", "error")
#             return render_template("signup.html")

#         users_collection.insert_one({
#             'name': name,
#             'email': email,
#             'password': password
#         })

#         session['user'] = email
#         return redirect(url_for('auth.option'))

#     return render_template("signup.html")

# @auth_bp.route('/google')
# def google_login():
#     if not google.authorized:
#         return redirect(url_for("google.login"))

#     resp = google.get("/oauth2/v2/userinfo")
#     if resp.ok:
#         info = resp.json()
#         email = info['email']
#         name = info.get('name', 'No Name')

#         user = users_collection.find_one({'email': email})
#         if not user:
#             # Create new Google user
#             result = users_collection.insert_one({
#                 'name': name,
#                 'email': email,
#                 'password': None,
#                 'study_time': {},
#                 'study_streak': 0
#             })
#             user_id = str(result.inserted_id)
#         else:
#             user_id = str(user['_id'])

#         session['user'] = {
#             'id': user_id,
#             'email': email
#         }

#         flash("Logged in with Google!", "success")
#         return redirect(url_for('dashboard.dashboard'))

#     flash("Failed to fetch Google user info.", "error")
#     return redirect(url_for('auth.login'))


# # Option page after signup
# @auth_bp.route('/option')
# def option():
#     if 'user' not in session:
#         return redirect(url_for('auth.login'))
#     return render_template("option.html")

# # Forgot password page
# @auth_bp.route('/forgot', methods=['GET', 'POST'])
# def forgot():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         user = users_collection.find_one({'email': email})

#         if user:
#             flash(f"A reset link has been sent to {email}", "success")
#         else:
#             flash("Email not found. Please check again.", "error")

#         return render_template("forgot.html")

#     return render_template("forgot.html")

#     token = secrets.token_urlsafe(32)
#     expires_at = datetime.utcnow() + timedelta(minutes=30)
#     users_collection.update_one({'email': email}, {'$set': {'reset_token': token, 'reset_token_expires': expires_at}})

#     # Replace this with real email sending
#     reset_link = f"http://localhost:5000/reset.html?token={token}"
#     print(f"Send this link via email: {reset_link}")

#     return jsonify({"success": True, "message": f"Reset link sent to {email}."})

# @auth_bp.route('/reset', methods=['POST'])
# def reset_password():
#     data = request.get_json()
#     token = data.get('token')
#     new_password = data.get('password')

#     user = users_collection.find_one({'reset_token': token})
#     if not user:
#         return jsonify({"success": False, "message": "Invalid token."})

#     if datetime.utcnow() > user['reset_token_expires']:
#         return jsonify({"success": False, "message": "Token expired."})

#     hashed_pw = generate_password_hash(new_password)
#     users_collection.update_one({'_id': user['_id']}, {'$set': {'password': hashed_pw}, '$unset': {'reset_token': "", 'reset_token_expires': ""}})

#     return jsonify({"success": True, "message": "Password reset successful."})


# # Logout
# @auth_bp.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('auth.login'))


from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask_dance.contrib.google import google
from app.models import users_collection
import secrets
from datetime import datetime, timedelta
import os

# Optional: verify Google ID tokens when using Google Identity Services (GSI)
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as grequests
except Exception:
    id_token = None
    grequests = None

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# =============================
# 🔐 LOGIN
# =============================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users_collection.find_one({'email': email})

        if user:
            # Verify hashed password (if exists)
            if user.get('password') and check_password_hash(user['password'], password):
                # ✅ Save user ObjectId as string in session
                session['user'] = {
                    'id': str(user['_id']),
                    'email': user['email']
                }
                flash("Login successful!", "success")
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash("Invalid password. Please try again.", "error")
        else:
            flash("Email not found. Please signup first.", "error")

    return render_template("login.html")


# =============================
# 📝 SIGNUP
# =============================

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("User already exists. Please login.", "error")
            return render_template("signup.html")

        # Hash password before storing
        hashed_password = generate_password_hash(password)

        # Insert new user
        result = users_collection.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password,
            'study_time': {},
            'study_streak': 0,
            'created_at': datetime.utcnow()
        })

        # ✅ Store session data (ObjectId as string) and consistent user dict
        user_id_str = str(result.inserted_id)
        session['user_id'] = user_id_str
        session['user'] = {'id': user_id_str, 'email': email}

        flash("Signup successful! Welcome to Smart Study Assistant.", "success")
        return redirect(url_for('auth.option'))

    return render_template("signup.html")



# =============================
# 🌐 GOOGLE LOGIN
# =============================
@auth_bp.route('/google', methods=['GET', 'POST'])
def google_login():
    # Support two Google login flows:
    # 1) Server-side OAuth (flask-dance) - GET
    # 2) Client-side Google Identity Services (GSI) - POST with ID token
    if request.method == 'POST':
        data = request.get_json() or {}
        credential = data.get('credential') or data.get('id_token')
        if not credential:
            return jsonify({'success': False, 'message': 'No credential provided'}), 400

        if not id_token or not grequests:
            return jsonify({'success': False, 'message': 'Server not configured to verify Google tokens.'}), 500

        CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        try:
            idinfo = id_token.verify_oauth2_token(credential, grequests.Request(), CLIENT_ID)
            email = idinfo.get('email')
            name = idinfo.get('name', 'No Name')

            if not email:
                return jsonify({'success': False, 'message': 'Email not available in token.'}), 400

            user = users_collection.find_one({'email': email})
            if not user:
                result = users_collection.insert_one({
                    'name': name,
                    'email': email,
                    'password': None,
                    'study_time': {},
                    'study_streak': 0,
                    'created_at': datetime.utcnow()
                })
                user_id = str(result.inserted_id)
            else:
                user_id = str(user['_id'])

            session['user'] = {'id': user_id, 'email': email}
            session['user_id'] = user_id
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Invalid token', 'error': str(e)}), 400

    # Fallback to flask-dance OAuth flow (redirect)
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        info = resp.json()
        email = info['email']
        name = info.get('name', 'No Name')

        user = users_collection.find_one({'email': email})

        if not user:
            result = users_collection.insert_one({
                'name': name,
                'email': email,
                'password': None,
                'study_time': {},
                'study_streak': 0,
                'created_at': datetime.utcnow()
            })
            user_id = str(result.inserted_id)
        else:
            user_id = str(user['_id'])

        session['user'] = {
            'id': user_id,
            'email': email
        }
        session['user_id'] = user_id

        flash("Logged in with Google!", "success")
        return redirect(url_for('dashboard.dashboard'))

    flash("Failed to fetch Google user info.", "error")
    return redirect(url_for('auth.login'))


# =============================
# ⚙️ OPTION PAGE
# =============================
@auth_bp.route('/option')
def option():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template("option.html")


# =============================
# 🔑 FORGOT PASSWORD
# =============================
@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        user = users_collection.find_one({'email': email})

        if user:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            users_collection.update_one(
                {'email': email},
                {'$set': {'reset_token': token, 'reset_token_expires': expires_at}}
            )

            # Create reset link
            reset_link = f"http://localhost:5000/reset?token={token}"
            
            # Send email
            from app.extensions import send_email
            subject = "Password Reset Request - Smart Study Assistant"
            body = f"""
Hello {user.get('name', 'User')},

We received a request to reset your password. Click the link below to reset it:

{reset_link}

This link will expire in 30 minutes.

If you didn't request this, please ignore this email.

Best regards,
Smart Study Assistant Team
            """
            
            if send_email(email, subject, body):
                flash(f"A password reset link has been sent to {email}. Check your inbox!", "success")
            else:
                flash("Failed to send email. Please try again later.", "error")
        else:
            flash("Email not found in our system.", "error")

    return render_template("forgot.html")


# =============================
# 🔄 RESET PASSWORD
# =============================
@auth_bp.route('/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    user = users_collection.find_one({'reset_token': token})
    if not user:
        return jsonify({"success": False, "message": "Invalid token."})

    if datetime.utcnow() > user['reset_token_expires']:
        return jsonify({"success": False, "message": "Token expired."})

    hashed_pw = generate_password_hash(new_password)
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'password': hashed_pw}, '$unset': {'reset_token': "", 'reset_token_expires': ""}}
    )

    return jsonify({"success": True, "message": "Password reset successful."})


# =============================
# 🚪 LOGOUT
# =============================
@auth_bp.route('/logout')
def logout():
    # Remove both representations from session for consistency
    session.pop('user', None)
    session.pop('user_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
