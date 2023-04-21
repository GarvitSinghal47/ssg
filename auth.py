from flask import Blueprint, render_template, url_for, redirect, request, flash,session,jsonify
from __init__ import User
from __init__ import db

# Essentials For Login Creation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

auth = Blueprint("auth", __name__)

# Routes


@auth.route("/login")
def login():
	return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
	if request.method == "POST":
		# Get values from Form
		email = request.form.get("email")
		password = request.form.get("password")
		remember = request.form.get("remember")

		# if it returns a user then email already exist and user exist hence check for password
		user = User.query.filter_by(email=email).first()
		
		# if password doesn't match then redirect
		if not user or not check_password_hash(user.password, password):
			flash("Please check your login details and try again")
			return redirect('/login')
		login_user(user, remember=remember)
		
		email = user.email
		
		session['user']=email
		print(session['user'])
        
		# if the password is valid for the user we redirect to the main app
		return redirect('/index')


@auth.route("/signup")
def signup():
	return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
	# Get values from form
	data=request.get_json()
	email = data["email"]
	name = data["name"]
	password = data["password"]

	

	# if it returns a user then email already exist hence redirect
	user = User.query.filter_by(email=email).first()
	if user:
		return jsonify({'success': True, 'message': 'Sign up successful'})

	# else create a new user
	new_user = User(email=email, name=name,
	                password=generate_password_hash(password, method='sha256'))

	# add new user to DB
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'success': True, 'message': 'Sign up successful'})


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
