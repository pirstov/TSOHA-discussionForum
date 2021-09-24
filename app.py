from flask import Flask
from flask import redirect, render_template, request, session

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