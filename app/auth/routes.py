from flask import Flask,Blueprint, request, session, render_template, redirect, url_for

from app.models import users_collection



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('home.html')


@auth_bp.route('/signup', methods=[ 'GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        print(email,password)

        
        user = users_collection.find_one({'email': email})
        if user:
            return "User already exists. Please login."

        # Insert new user
        users_collection.insert_one({'email': email, 'password': password})

        return redirect(url_for('auth.login'))

    return redirect(url_for("auth.signup"))



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({'email': email, 'password': password})

        if user:
            # ✅ Store session
            session['user'] = email
            return redirect(url_for('dashboard.dashboard'))
        else:
            return "Invalid credentials. Please try again."
        
    if 'user' in session:
         return redirect(url_for('dashboard.dashboard'))

    return redirect(url_for("auth.login"))



@auth_bp.route('/logout')
def logout():
    session.pop('user', None) 
    return render_template("home.html")





# from flask import Flask, Blueprint, request, session, render_template, redirect, url_for
# from app.models import users_collection

# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# @auth_bp.route('/')
# def home():
#     return render_template('home.html')


# @auth_bp.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form.get("email")
#         password = request.form.get("password")

#         # Check if email already exists
#         user = users_collection.find_one({'email': email})
#         if user:
#             return "User already exists. Please login."

#         # Insert new user
#         users_collection.insert_one({'email': email, 'password': password})

#         return redirect(url_for('auth.login'))

#     return render_template('signup.html')


# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get("email")
#         password = request.form.get("password")

#         user = users_collection.find_one({'email': email, 'password': password})

#         if user:
#             session['user'] = email
#             return redirect(url_for('dashboard.dashboard'))
#         else:
#             return "Invalid credentials. Please try again."

#     return render_template("login.html")


# @auth_bp.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('auth.login'))
