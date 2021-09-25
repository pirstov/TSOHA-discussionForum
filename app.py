# Flask-related libraries
from logging import debug
from flask import Flask
from flask import redirect, render_template, request, session

# Database related library
from flask_sqlalchemy import SQLAlchemy

# For hashing the passwords
from werkzeug.security import check_password_hash, generate_password_hash

# For generating a secret key
import secrets
SECRET_KEY = secrets.token_hex(16)

# Create a Flask object
app = Flask(__name__)
# Add a secret key that was just generated
# ----------------------------------------------------
# TBD: Implement the secret key in the environment file 
# -----------------------------------------------------
app.secret_key = SECRET_KEY

# Define the database location for the app
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///ville"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Root page
@app.route("/")
def index():
	# Query the DB for different sections
	# --------------------------------------------
	# TBD: implement querying for the number of threads in the section
	# --------------------------------------------
	result = db.session.execute("SELECT S.id, S.section_name, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
								" max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
								"LEFT JOIN messages M on T.id = M.thread_id GROUP BY S.id")
	section_names = result.fetchall()
	return render_template("index.html", sections = section_names)

# User registration page
@app.route("/register")
def register():
	return render_template("register.html")

# Account creation process
@app.route("/createaccount", methods=["POST"])
def createaccount():
	username = request.form["username"]
	# generate the hash for the password directly
	password = generate_password_hash(request.form["password"])

	# ----------------------------------
	# TBD: implement functionality to check if the username is already in use
	# ----------------------------------

	# Insert the new user into the appropriate database table
	sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
	db.session.execute(sql, {"username":username, "password":password})
	db.session.commit()

	return redirect("/")

# Log in page
@app.route("/loginpage")
def loginpage():
	return render_template("loginpage.html")

# Log in information processing
@app.route("/login", methods=["POST"])
def login():
	username = request.form["username"]
	password = request.form["password"]

	# ------------------------------------------
	# TBD: implement validity check of the input
	# ------------------------------------------

	session["username"] = username
	return redirect("/")

# Log out processing
@app.route("/logout")
def logout():
	del session["username"]
	return redirect("/")

# pages for different sections
@app.route("/section/<id>")
def section(id):
	# -----------------------------------------------
	# TBD: Implement counting of messages within each thread
	# TBD: Implement inclusion of the section name to section.html
	# -----------------------------------------------
	sql = "SELECT id, posting_time, thread_name FROM threads where section_id=:id"
	result = db.session.execute(sql, {"id": id})
	threads = result.fetchall()
	return render_template("section.html", section_name = id, threads = threads)
