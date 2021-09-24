# Flask-related libraries
from logging import debug
from flask import Flask
from flask import redirect, render_template, request, session

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

# Root page
@app.route("/")
def index():
	return render_template("index.html")

# User registration page
@app.route("/register")
def register():
	pass

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
	db.session.execute(sql, {"username":username, "pasword":password})
	db.session.commit()

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