# Flask-related libraries
from logging import debug
from flask import Flask
from flask import redirect, render_template, request, session

# For formatting time stamp printing
from datetime import datetime

# For configuring flask through the .env file
from os import getenv

# Database related library
from flask_sqlalchemy import SQLAlchemy

# For hashing the passwords
from werkzeug.security import check_password_hash, generate_password_hash

# Create a Flask object
app = Flask(__name__)
# Configure according to the environment file
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

# Define the database location for the app
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Root page
@app.route("/")
def index():
	# Query the DB for different sections
	result = db.session.execute("SELECT S.id, S.section_name, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
								" max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
								"LEFT JOIN messages M on T.id = M.thread_id GROUP BY S.id")
	section_names = result.fetchall()
	return render_template("index.html", sections = section_names)

# User registration page
@app.route("/register")
def register():
	return render_template("register.html", error=None)

# Account creation process
@app.route("/createaccount", methods=["POST"])
def createaccount():
	username = request.form["username"]
	# generate the hash for the password directly
	password = generate_password_hash(request.form["password"])

	# Check if the username is already in use
	sql = "SELECT count(*) FROM users WHERE username = :username"
	result = db.session.execute(sql, {"username":username})
	usernameAvailable = result.fetchone()["count"] == 0

	if usernameAvailable:
		# Insert the new user into the appropriate database table
		sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
		db.session.execute(sql, {"username":username, "password":password})
		db.session.commit()

		# Return to the front page
		return redirect("/")
	else:
		# refresh the account creation page with an error message
		error = 'Username already in use!'
		return render_template("register.html", error=error)

# Log in page
@app.route("/loginpage")
def loginpage():
	return render_template("loginpage.html", error=None)

# Log in information processing
@app.route("/login", methods=['POST'])
def login():

	username = request.form["username"]
	password = request.form["password"]

	# Check the validity of the input
	sql = "SELECT id, password FROM users WHERE username =:username"
	result = db.session.execute(sql, {"username": username})
	user = result.fetchone()

	#print(user)
	if not user:
		error = "Invalid username"
		return render_template("loginpage.html", error=error)
	else:
		session["username"] = username
		return redirect("/")

# Log out processing
@app.route("/logout")
def logout():
	del session["username"]
	return redirect("/")

# Pages for different sections
@app.route("/section/<id>")
def section(id):
	# -----------------------------------------------
	# TBD: Implement counting of messages within each thread
	# -----------------------------------------------
	sql = "SELECT T.id, T.posting_time, T.thread_name, S.section_name FROM threads T left join sections S on T.section_id = S.id WHERE section_id=:id"
	result = db.session.execute(sql, {"id": id})
	threads = result.fetchall()
	return render_template("section.html", id = id, threads = threads)

# Pages for different threads
@app.route("/section/<id>/<thread_id>")
def thread(id, thread_id):
	# -------------------------------------------
	# TBD: Implement presenting each thread as a chain of messages
	# -------------------------------------------
	return render_template("thread.html")