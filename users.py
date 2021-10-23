from db import db

# Flask-related libraries
#from logging import debug
#from flask import Flask
#from flask import abort
from flask import redirect, render_template, request, session

# For formatting time stamp printing
#from datetime import datetime

# For configuring flask through the .env file
#from os import getenv

# Database related library
#from flask_sqlalchemy import SQLAlchemy

# For hashing the passwords
from werkzeug.security import check_password_hash, generate_password_hash

# For generating crsf tokens
import secrets


def createAccount(username, password):

    # generate the hash for the password
	password = generate_password_hash(password)

	# Check if the username is already in use
	sql = "SELECT count(*) FROM users WHERE username = :username"
	result = db.session.execute(sql, {"username":username})
	usernameAvailable = (result.fetchone()["count"] == 0)

	if usernameAvailable:
		# Insert the new user into the appropriate database table
		sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
		db.session.execute(sql, {"username":username, "password":password})
		db.session.commit()

		# Registration successful
		return True
	else:
        # Registration failed, username in use
		return False

def login(username, password):
    # Check the validity of the input
	sql = "SELECT id, password FROM users WHERE username =:username"
	result = db.session.execute(sql, {"username": username})
	user = result.fetchone()
	# Check that an account with the input username is found
	if not user:
		#error = "Invalid username or password"
		return False

	# NOTE: THIS IS TEMPORARY CODE BLOCK FOR CHECKING FUNCTIONALITY
	# -------------------------------------------------------------
	if username == "root":
		user_password = generate_password_hash("root")
	elif username == "tester":
		user_password = generate_password_hash("123")
	else:
		user_password = user.password
	# --------------------------------------------------------------

	# Check the correctness of password
	if check_password_hash(user_password, password):
		# Set the session username
		session["username"] = username
		# Set a crsf_token for the user to prevent exploitation of CRSF vulnerability
		session["crsf_token"] = secrets.token_hex(16)
		# Login successful
		return True
	else:
		# Login failed, incorrect password
		return False

    