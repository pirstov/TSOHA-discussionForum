from db import db

from flask import session

# For hashing the passwords
from werkzeug.security import check_password_hash, generate_password_hash

# For generating crsf tokens
import secrets


def create_account(username, password):

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

def logout():

    del session["username"]

def is_moderator():
    if not "username" in session:
        return False
    else:
        sql = "SELECT moderator FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username": session["username"]})
        isModerator = result.fetchone().moderator
        if isModerator:
            return True
        else:
            return False

def crsf_token_valid(crsf_token_input):

    if session["crsf_token"] != crsf_token_input:
        return False
    else:
        return True

def promote_user(username):

    # Check that the typed in string is an actual username
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if not user:
        return False

    # A valid username is input, promote
    sql = "UPDATE users SET moderator=true WHERE id=:user_id"
    db.session.execute(sql, {"user_id": user.id})
    db.session.commit()

    return True

def check_section_access(section_id):

    sql = "SELECT private FROM sections WHERE id=:section_id"
    result = db.session.execute(sql, {"section_id": section_id})
    isPrivate = result.fetchone().private

    if isPrivate:
        if not "username" in session:
            # The section is private but the user is not logged in, no access
            return False
        # The section is private and the user is logged in, access privileges have to be checked
        user_id = get_user_id()

        sql = "SELECT id FROM user_privileges WHERE section_id=:section_id AND user_id=:user_id"
        result = db.session.execute(sql, {"section_id":section_id, "user_id":user_id})
        hasAccess = result.fetchone()
        if hasAccess:
            return True
        else:
            return False
    else:
        # The section is not private, access is granted
        return True

def is_existing_username(username):

    # Check that the typed in string is an actual username
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if user:
        return True
    else:
        return False

def grant_private_section_access(username, section_id):

    user_id = get_user_id(username)
    sql = "INSERT INTO user_privileges (user_id, section_id) VALUES (:user_id, :section_id)"
    db.session.execute(sql, {"user_id":user_id, "section_id": section_id})
    db.session.commit()


def get_user_id(username = None):
    if not username:
        if not "username" in session:
            return 0
        username = session["username"]

    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    userId = result.fetchone().id
    
    return userId
