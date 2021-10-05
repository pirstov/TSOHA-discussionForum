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

	# Query for the section name based on the id
	sql = "SELECT section_name FROM sections WHERE id=:id"
	result = db.session.execute(sql, {"id":id})
	section_name = result.fetchone().section_name

	# Query for the thread id, posting time, thread name, and username of the poster for each thread
	sql = "SELECT T.id, T.posting_time, T.thread_name, U.username FROM threads T"\
	" LEFT JOIN users U ON T.user_id = U.id WHERE T.section_id=:id ORDER BY T.posting_time DESC"
	result = db.session.execute(sql, {"id": id})
	threads = result.fetchall()
	
	return render_template("section.html", id = id, threads = threads, section_name = section_name)

# Thread creation page
@app.route("/section/<id>/createthread")
def createthread(id):
	return render_template("createthread.html", id = id)

# Posting the thread to the database
@app.route("/section/<id>/post_thread", methods = ["POST"])
def post_thread(id):
	threadTitle = request.form["threadTitle"]
	message = request.form["content"]

	# Query for the user id
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username": session["username"]})
	user_id = result.fetchone()["id"]

	# Insert thread into database
	sql = "INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), :user_id, :id, :threadTitle, :message) RETURNING id"
	result = db.session.execute(sql, {"user_id":user_id, "id":id, "threadTitle":threadTitle, "message":message})
	db.session.commit()
	thread_id = result.fetchone()[0]

	return redirect("/section/" + str(id) + "/" + str(thread_id))

# Pages for different threads
@app.route("/section/<id>/<thread_id>")
def thread(id, thread_id):
	# Query for the thread name and content
	sql = "SELECT T.thread_name, T.posting_time, T.content, U.username FROM threads T LEFT JOIN users U ON T.user_id = U.id WHERE T.id=:thread_id"
	result = db.session.execute(sql, {"thread_id":thread_id})
	thread = result.fetchone()

	# Query for the messages posted in the thread
	sql = "SELECT M.id, M.posting_time, M.content, U.username FROM messages M" \
	      " LEFT JOIN users U ON U.id = M.user_id WHERE M.thread_id = :thread_id ORDER BY posting_time ASC"
	result = db.session.execute(sql, {"thread_id": thread_id})
	messages = result.fetchall()

	return render_template("thread.html", messages = messages, id=id, thread_id = thread_id, thread = thread)

# Page for writing a reply to a thread
@app.route("/section/<id>/<thread_id>/reply")
def reply(id, thread_id):
	return render_template("reply.html", id=id, thread_id=thread_id)

# Processing of the reply written to a thread
@app.route("/section/<id>/<thread_id>/post_reply", methods = ["POST"])
def post_reply(id, thread_id):
	content = request.form["content"]

	# Query for the user id
	sql = "SELECT id FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username": session["username"]})
	user_id = result.fetchone()["id"]

	# Insert the reply into the database
	sql = "INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), :user_id, :thread_id, :content)"
	db.session.execute(sql, {"user_id": user_id, "thread_id": thread_id, "content": content})
	db.session.commit()

	print(thread_id)

	return redirect("/section/" + str(id) + "/" + str(thread_id))


# Editing a thread
@app.route("/section/<id>/<thread_id>/edit_thread")
def edit_thread(id, thread_id):
	# Query for the thread name and content
	sql = "SELECT thread_name, content FROM threads where id=:thread_id"
	result = db.session.execute(sql, {"thread_id":thread_id})
	thread = result.fetchone()

	return render_template("editthread.html", id = id, thread_id = thread_id, thread = thread)

# Updating the thread database according to the edits
@app.route("/section/<id>/<thread_id>/post_thread_edit", methods = ["POST"])
def post_thread_edit(id, thread_id):
	thread_name = request.form["threadTitle"]
	content     = request.form["content"]
	# Update the thread database table accordingly
	sql = "UPDATE threads SET thread_name=:thread_name, content=:content WHERE id=:thread_id"
	db.session.execute(sql, {"thread_name":thread_name, "content":content, "thread_id":thread_id})
	db.session.commit()

	return redirect("/section/" + str(id) + "/" + str(thread_id))

# Editing a message in a thread
@app.route("/section/<id>/<thread_id>/<message_id>/edit_message")
def edit_message(id, thread_id, message_id):
	# Query for the message and content
	sql = "SELECT content FROM messages WHERE id=:message_id"
	result = db.session.execute(sql, {"message_id": message_id})
	message = result.fetchone()

	return render_template("editmessage.html", id=id, thread_id = thread_id, message_id = message_id, message = message)

# Updating the message database according to the edits
@app.route("/section/<id>/<thread_id>/<message_id>/post_message_edit", methods = ["POST"])
def post_message_edit(id, thread_id, message_id):
	content = request.form["content"]
	# Update the message database table accordingly
	sql = "UPDATE messages SET content=:content WHERE id=:message_id"
	db.session.execute(sql, {"content":content, "message_id":message_id})
	db.session.commit()

	return redirect("/section/" + str(id) + "/" + str(thread_id))
