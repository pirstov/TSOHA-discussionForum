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

# A helper function for checking if the user has access to the URL that is accessed
def check_privileges(section_id, username = None):
	sql = "SELECT private FROM sections WHERE id=:section_id"
	result = db.session.execute(sql, {"section_id": section_id})
	isPrivate = result.fetchone().private
	if isPrivate:
		if not username:
			# The section is private but the user is not logged in, no access
			return False
		# The section is private and the user is logged in, access privileges have to be checked
		sql = "SELECT id FROM users WHERE username=:username"
		result = db.session.execute(sql, {"username":username})
		user_id = result.fetchone().id

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

# Root page
@app.route("/")
def index():
	# Set the session url in case the user is not yet logged in
	if not "username" in session:
		session["url"] = "/"

	# Query the database for different sections
	if "username" in session:
		# Fetch the user id of the logged in user
		sql = "SELECT id FROM users WHERE username=:username"
		result = db.session.execute(sql, {"username":session["username"]})
		user = result.fetchone()
		# Query for the sections that are not private or private to which the user has privilege
		sql = "SELECT S.id, S.section_name, S.private, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
			  " max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
			  "LEFT JOIN messages M on T.id = M.thread_id WHERE S.visible=true "\
			  "GROUP BY S.id HAVING (NOT S.private OR S.id IN (SELECT section_id FROM user_privileges WHERE user_id=:user_id))"
		result = db.session.execute(sql, {"user_id":user.id})
	else:
		# The user is not logged in, fetch sections that are not private
		result = db.session.execute("SELECT S.id, S.section_name, S.private, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
								" max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
								"LEFT JOIN messages M on T.id = M.thread_id WHERE S.visible=true AND S.private=false GROUP BY S.id")
	section_names = result.fetchall()

	if "username" in session:
		# If the user is logged in, check for moderator rights
		sql = "SELECT moderator FROM users WHERE username=:username"
		result = db.session.execute(sql, {"username":session["username"]})
		isModerator = result.fetchone()[0] == True
	else:
		isModerator = False
	
	# Render the front page
	return render_template("index.html", sections = section_names, isModerator = isModerator)


# User registration page
@app.route("/register")
def register():

	# Render the registration page
	return render_template("register.html", error=None, prevURL = session["url"])


# Account creation process
@app.route("/createaccount", methods=["POST"])
def createaccount():

	username = request.form["username"]
	password = request.form["password"]

	# Check that both the username and password are input
	if not username or not password:
		error = "Please type in both the username and password"
		return render_template("register.html", error=error, prevURL = session["url"])

	# generate the hash for the password
	password = generate_password_hash(password)

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


# Login page
@app.route("/loginpage")
def loginpage():
	# Render the login page
	return render_template("loginpage.html", error=None, prevURL = session["url"])


# Log in information processing
@app.route("/login", methods=['POST'])
def login():

	username = request.form["username"]
	password = request.form["password"]

	# Check if something has been input
	if not username or not password:
		error = "Please type in both the username and password"
		return render_template("loginpage.html", error=error, prevURL = session["url"])

	# Check the validity of the input
	sql = "SELECT id, password FROM users WHERE username =:username"
	result = db.session.execute(sql, {"username": username})
	user = result.fetchone()

	# NOTE: THIS IS TEMPORARY CODE BLOCK FOR CHECKING FUNCTIONALITY
	# -------------------------------------------------------------
	if username == "root":
		user_password = generate_password_hash("root")
	elif username == "tester":
		user_password = generate_password_hash("123")
	else:
		user_password = user.password
	# --------------------------------------------------------------

	if not user:
		error = "Invalid username"
		# Refresh the login page with an error message
		return render_template("loginpage.html", error=error)
	else:
		# Check the correctness of password
		if check_password_hash(user_password, password):
			session["username"] = username
			if "url" in session:
				return redirect(session["url"])
			# Login succesful, render the front page
			return redirect("/")
		else:
			error = "Invalid password"
			# Refresh the login page with an error message
			return render_template("loginpage.html", error=error)


# Log out processing
@app.route("/logout")
def logout():
	
	# Delete the current session
	del session["username"]
	# Render the front page
	return redirect("/")


# Pages for different sections
@app.route("/section/<id>")
def section(id):
	# Set the session url in case the user is not yet logged in
	if not "username" in session:
		session["url"] = "/section/" + str(id)
		isModerator = False
		hasAccess = check_privileges(id)
	else:
		# User is logged in, check if moderator
		sql = "SELECT moderator FROM users where username=:username"
		result = db.session.execute(sql, {"username":session["username"]})
		isModerator = result.fetchone().moderator
		# Check if access to private section
		hasAccess = check_privileges(id, session["username"])

	# Query for the section name based on the id
	sql = "SELECT section_name, private FROM sections WHERE id=:id"
	result = db.session.execute(sql, {"id":id})
	section = result.fetchone()

	# Query for the thread id, posting time, thread name, and username of the poster for each thread
	sql = "SELECT T.id, T.posting_time, T.thread_name, U.username FROM threads T"\
	" LEFT JOIN users U ON T.user_id = U.id WHERE T.section_id=:id AND T.visible=true ORDER BY T.posting_time DESC"
	result = db.session.execute(sql, {"id": id})
	threads = result.fetchall()
	
	# Render the appropriate section page
	return render_template("section.html", id = id, threads = threads, section = section, isModerator=isModerator, hasAccess = hasAccess)

# Thread creation page
@app.route("/section/<id>/createthread")
def createthread(id):
	if not "username" in session:
		hasAccess = False
	else:
		hasAccess = check_privileges(id, session["username"])
	
	# Render the thread creation page
	return render_template("createthread.html", id = id, error=None, hasAccess = hasAccess)


# Posting the thread to the database
@app.route("/section/<id>/post_thread", methods = ["POST"])
def post_thread(id):

	threadTitle = request.form["threadTitle"]
	message = request.form["content"]

	# Make sure that a title and message is provided
	if not threadTitle or not message:
		error = "Please include both the thread and a message"
		return render_template("createthread.html", id=id, error=error, hasAccess=True)

	# Query for the user id
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username": session["username"]})
	user_id = result.fetchone()["id"]

	# Insert thread into database
	sql = "INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), :user_id, :id, :threadTitle, :message) RETURNING id"
	result = db.session.execute(sql, {"user_id":user_id, "id":id, "threadTitle":threadTitle, "message":message})
	db.session.commit()
	thread_id = result.fetchone()[0]

	# Render the page for the created thread
	return redirect("/section/" + str(id) + "/" + str(thread_id))


# Pages for different threads
@app.route("/section/<id>/<thread_id>")
def thread(id, thread_id):
	# Set the session url in case the user is not yet logged in
	if not "username" in session:
		session["url"] = "/section/" + str(id) + "/" + str(thread_id)
		hasAccess = check_privileges(id)
	else:
		# User is logged in, check if access rights are ok
		sql = "SELECT id, moderator FROM users where username=:username"
		result = db.session.execute(sql, {"username":session["username"]})
		user = result.fetchone()
		# Check if access to private section
		hasAccess = check_privileges(id, session["username"])

	# Query for the thread name and content
	sql = "SELECT T.thread_name, T.posting_time, T.content, U.username FROM threads T LEFT JOIN users U ON T.user_id = U.id WHERE T.id=:thread_id"
	result = db.session.execute(sql, {"thread_id":thread_id})
	thread = result.fetchone()

	# Query for the messages posted in the thread
	sql = "SELECT M.id, M.posting_time, M.content, U.username FROM messages M" \
	      " LEFT JOIN users U ON U.id = M.user_id WHERE M.thread_id=:thread_id AND M.visible=true ORDER BY posting_time ASC"
	result = db.session.execute(sql, {"thread_id": thread_id})
	messages = result.fetchall()

	# Render the appropriate thread page
	return render_template("thread.html", messages = messages, id=id, thread_id = thread_id, thread = thread, hasAccess = hasAccess)


# Page for writing a reply to a thread
@app.route("/section/<id>/<thread_id>/reply")
def reply(id, thread_id):
	if not "username" in session:
		hasAccess = False
	else:
		hasAccess = check_privileges(id, session["username"])

	# Render the reply creation page
	return render_template("reply.html", id=id, thread_id=thread_id, error=None, hasAccess=hasAccess)


# Processing of the reply written to a thread
@app.route("/section/<id>/<thread_id>/post_reply", methods = ["POST"])
def post_reply(id, thread_id):

	content = request.form["content"]

	# Check that the reply is not empty
	if not content:
		error = "Empty replies are not allowed"
		return render_template("reply.html", id=id, thread_id = thread_id, error=error, hasAccess = True)	

	# Query for the user id
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username": session["username"]})
	user_id = result.fetchone()["id"]

	# Insert the reply into the database
	sql = "INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), :user_id, :thread_id, :content)"
	db.session.execute(sql, {"user_id": user_id, "thread_id": thread_id, "content": content})
	db.session.commit()

	# Return to the replied thread
	return redirect("/section/" + str(id) + "/" + str(thread_id))


# Editing a thread
@app.route("/section/<id>/<thread_id>/edit_thread")
def edit_thread(id, thread_id):
	if not "username" in session:
		hasAccess = False
	else:
		hasAccess = check_privileges(id, session["username"])
		# Also check that the user is actually the creator of the thread
		sql = "SELECT U.username FROM threads T LEFT JOIN users U on T.user_id = U.id WHERE T.id=:thread_id"
		result = db.session.execute(sql, {"thread_id": thread_id})
		user = result.fetchone().username
		hasAccess = hasAccess and (user == session["username"])

	# Query for the thread name and content
	sql = "SELECT thread_name, content FROM threads where id=:thread_id"
	result = db.session.execute(sql, {"thread_id":thread_id})
	thread = result.fetchone()

	# Go to the thread editing page
	return render_template("editthread.html", id = id, thread_id = thread_id, thread = thread, error=None, hasAccess=hasAccess)


# Updating the thread database according to the edits
@app.route("/section/<id>/<thread_id>/post_thread_edit", methods = ["POST"])
def post_thread_edit(id, thread_id):

	thread_name = request.form["threadTitle"]
	content     = request.form["content"]

	# Check that a title and message are written
	if not thread_name or not content:
		error = "Please include both the thread title and message"
		thread = {"thread_name": thread_name, "content": content}
		return render_template("editthread.html", id=id, thread_id = thread_id, thread=thread, error=error, hasAccess=True)
	
	# Update the thread database table accordingly
	sql = "UPDATE threads SET thread_name=:thread_name, content=:content WHERE id=:thread_id"
	db.session.execute(sql, {"thread_name":thread_name, "content":content, "thread_id":thread_id})
	db.session.commit()

	# Return to the edited thread
	return redirect("/section/" + str(id) + "/" + str(thread_id))


# Editing a message in a thread
@app.route("/section/<id>/<thread_id>/<message_id>/edit_message")
def edit_message(id, thread_id, message_id):

	# Check if the user has rights to edit the message
	if not "username" in session:
		hasAccess = False
	else:
		hasAccess = check_privileges(id, session["username"])
		# Check also that the user is the creator of the message
		sql = "SELECT U.username FROM messages M LEFT JOIN users U on M.user_id = U.id WHERE M.id=:message_id"
		result = db.session.execute(sql, {"message_id": message_id})
		user = result.fetchone().username
		hasAccess = hasAccess and (user == session["username"])

	# Query for the current content of the edited message
	sql = "SELECT content FROM messages WHERE id=:message_id"
	result = db.session.execute(sql, {"message_id": message_id})
	message = result.fetchone()

	# Go to the editing page
	return render_template("editmessage.html", id=id, thread_id = thread_id, message_id = message_id, message = message, error=None, hasAccess=hasAccess)


# Updating the message database according to the edits
@app.route("/section/<id>/<thread_id>/<message_id>/post_message_edit", methods = ["POST"])
def post_message_edit(id, thread_id, message_id):

	content = request.form["content"]

	# Check that something has been written
	if not content:
		error = "Please add a message"
		return render_template("editmessage.html", id=id, thread_id=thread_id, message_id=message_id, message=None, error=error, hasAccess=True)
	
	# Update the message database table accordingly
	sql = "UPDATE messages SET content=:content WHERE id=:message_id"
	db.session.execute(sql, {"content":content, "message_id":message_id})
	db.session.commit()

	# Return to the thread
	return redirect("/section/" + str(id) + "/" + str(thread_id))


# Deleting a message in a thread
@app.route("/section/<id>/<thread_id>/<message_id>/delete_message")
def delete_message(id, thread_id, message_id):
	# Check that the user is actually the one who wrote the message
	if not "username" in session:
		return redirect("/section/" + str(id) + "/" + str(thread_id))
	else:
		# Check that the user is actually the one who wrote the message
		sql = "SELECT U.username FROM messages M LEFT JOIN users U ON m.user_id = U.id WHERE m.id=:message_id"
		result = db.session.execute(sql, {"message_id": message_id})
		user = result.fetchone().username
		if (user == session["username"]):
			# If the user matches, set the visibility of the deleted message to false
			sql = "UPDATE messages SET visible=false WHERE id=:message_id"
			db.session.execute(sql, {"message_id": message_id})
			db.session.commit()

		# Return to the thread
		return redirect("/section/" + str(id) + "/" + str(thread_id))


# Deleting a thread and all its associated messages
@app.route("/section/<id>/<thread_id>/delete_thread")
def delete_thread(id, thread_id):
	# Check that the user is actually the one who wrote the thread
	if not "username" in session:
		return redirect("/section/" + str(id) + "/" + str(thread_id))
	else:
		# Check that the user is correct
		sql = "SELECT U.username FROM threads T LEFT JOIN users U on T.user_id=U.id WHERE T.id=:thread_id"
		result = db.session.execute(sql, {"thread_id": thread_id})
		user = result.fetchone().username
		if (user == session["username"]):
			# If the user matches, set the visibility of every message in the thread to false
			sql = "UPDATE messages SET visible=false WHERE thread_id=:thread_id"
			db.session.execute(sql, {"thread_id":thread_id})
			db.session.commit()

			# Set the visibility of the thread to false
			sql = "UPDATE threads SET visible=false WHERE id=:thread_id"
			db.session.execute(sql, {"thread_id":thread_id})
			db.session.commit()

			# Return to the section of the deleted thread
			return redirect("/section/" + str(id))
		else:
			return redirect("/section/" + str(id) + "/" + str(thread_id))


# Processing of search results 
@app.route("/result", methods=["GET"])
def result():

	query = request.args["query"].lower()
	prevURL = request.args["prevURL"]

	# Search for messages containing the queried string
	sql = "SELECT M.content, S.id AS section_id, T.id AS thread_id, T.thread_name FROM sections S " \
	      " LEFT JOIN threads T ON S.id=T.section_id LEFT JOIN messages M" \
	      " ON T.id = M.thread_id WHERE lower(M.content) LIKE :query"
	result = db.session.execute(sql, {"query": "%"+query+"%"})
	messages = result.fetchall()

	# Search for threads containing the queried string
	sql = "SELECT id, section_id, thread_name, content FROM threads WHERE (lower(content) LIKE :query) OR (lower(thread_name) LIKE :query)"
	result = db.session.execute(sql, {"query": "%"+query+"%"})
	threads = result.fetchall()

	# Render a page for the query results
	return render_template("result.html", messages=messages, threads=threads, prevURL = prevURL)

# Creation of sections
@app.route("/createsection")
def createsection():
	if not "username" in session:
		hasAccess = False
	else:
		# Check if the user is a moderator
		sql = "SELECT moderator FROM users WHERE username=:username"
		result = db.session.execute(sql, {"username":session["username"]})
		hasAccess = result.fetchone().moderator

	# Render the section creation page
	return render_template("createsection.html", error=None, hasAccess=hasAccess)

# Adding the section to the database table
@app.route("/post_section", methods=["POST"])
def post_section():

	section_name = request.form["sectionName"]

	# Check that a name is given for the section
	if not section_name:
		error = "Please input a name for the section"
		return render_template("createsection.html", error=error, hasAccess=True)

	makePrivate = request.form.getlist("makePrivate")
	
	# create a boolean variable based on whether the 
	# sections is to be made private
	make_private = len(makePrivate) == 1

	sql = "INSERT INTO sections (section_name, private) VALUES (:section_name, :make_private) RETURNING id"
	result = db.session.execute(sql, {"section_name": section_name, "make_private": make_private})
	section = result.fetchone()

	# If the newly created section is private, grant the creator access to it
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username": session["username"]})
	user = result.fetchone()

	sql = "INSERT INTO user_privileges (user_id, section_id) VALUES (:user_id, :section_id)"
	db.session.execute(sql, {"user_id":user.id, "section_id":section.id})
	db.session.commit()

	return redirect("/")

# Deleting a section
@app.route("/deletesection/<section_id>")
def deletesection(section_id):
	if "username" in session:
		if check_privileges(section_id, session["username"]):
			# Update the visible value of the deleted section to false 
			sql = "UPDATE sections SET visible=false WHERE id=:section_id"
			db.session.execute(sql, {"section_id": section_id})
			db.session.commit()
			
	# Render the front page
	return redirect("/")

# Granting a user moderator rights
@app.route("/promoteuser")
def promoteuser():
	if not "username" in session:
		return redirect("/")
	else:
		sql = "SELECT moderator FROM users WHERE username=:username"
		result = db.session.execute(sql, {"username": session["username"]})
		user = result.fetchone().moderator
		if user:
			# Render the user promotion page
			return render_template("promoteuser.html", error=None)
		else:
			return redirect("/")
		

# Applying the promotion to the user table
@app.route("/applyPromotion", methods=["POST"])
def applyPromotion():

	username = request.form["username"]

	# Check that something is typed in
	if not username:
		error = "Please type in a username"
		return render_template("promoteuser.html", error=error)

	# Check that the typed in string is an actual username
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username":username})
	user = result.fetchone()

	if not user:
		error = "Username not found"
		return render_template("promoteuser.html", error=error)

	# A valid username is input, promote
	sql = "UPDATE users SET moderator=true WHERE id=:user_id"
	db.session.execute(sql, {"user_id": user.id})
	db.session.commit()

	return redirect("/")

# Granting a user moderator rights
@app.route("/<id>/grantuseraccess")
def grantuseraccess(id):
	if not "username" in session:
		hasAccess = check_privileges(id)
	else:
		hasAccess = check_privileges(id, session["username"])

	# Query for the section name corresponding to the id
	sql = "SELECT section_name FROM sections WHERE id=:section_id"
	result = db.session.execute(sql, {"section_id": id})
	section = result.fetchone()

	# Render the user promotion page
	return render_template("grantuseraccess.html", id=id, section_name = section.section_name, error=None, hasAccess=hasAccess)


# Applying the user access to the private section
@app.route("/<id>/applyuseraccess", methods=["POST"])
def applyuseraccess(id):

	username = request.form["username"]

	# Check that something is typed in
	if not username:
		error = "Please type in a username"
		sql = "SELECT section_name FROM sections WHERE id=:section_id"
		result = db.session.execute(sql, {"section_id":id})
		section = result.fetchone()
		return render_template("grantuseraccess.html", id = id, section_name = section.section_name, error=error, hasAccess=True)

	# Check that the typed in string is an actual username
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username":username})
	user = result.fetchone()

	if not user:
		error = "Username not found"
		sql = "SELECT section_name FROM sections WHERE id=:section_id"
		result = db.session.execute(sql, {"section_id":id})
		section = result.fetchone()
		return render_template("grantuseraccess.html", id = id, section_name = section.section_name, error=error, hasAccess=True)

	# A valid username is input, grant access
	sql = "INSERT INTO user_privileges (user_id, section_id) VALUES (:user_id, :section_id)"
	db.session.execute(sql, {"user_id":user.id, "section_id": id})
	db.session.commit()

	return redirect("/section/" + str(id))