from app import app
from db import db

import users, forum

#from flask import Flask
from flask import abort
from flask import redirect, render_template, request, session

# For formatting time stamp printing
from datetime import datetime

# Root page
@app.route("/")
def index():

    if not "username" in session:
        # Set the session url in case the user is not yet logged in
        session["url"] = "/"
    
    # Check whether the user is a moderator
    isModerator = users.is_moderator()

    # Fetch the sections that are accessible to the user
    sections = forum.list_sections()

    return render_template("index.html", sections = sections, isModerator = isModerator)


# User registration page
@app.route("/register")
def register():

	return render_template("register.html", error=  None, prevURL = session["url"])


# Account creation process
@app.route("/createaccount", methods=["POST"])
def createaccount():

    username = request.form["username"]
    password = request.form["password"]

	# Check that both the username and password are input
    if not username or not password:
        error = "Please type in both the username and password"
        return render_template("register.html", error = error, prevURL = session["url"])

    if users.create_account(username, password):
        # Account creation successful
        return redirect("/")
    else:
        # Account creation unsuccesful, provide the user an error message
        error = "Username already in use"
        return render_template("register.html", error = error)

# Login page
@app.route("/loginpage")
def loginpage():

	return render_template("loginpage.html", error = None, prevURL = session["url"])


# Log in information processing
@app.route("/login", methods=['POST'])
def login():
    username = request.form["username"]
    password = request.form["password"]

	# Check if something has been input
    if not username or not password:
        error = "Please type in both the username and password"
        return render_template("loginpage.html", error=error, prevURL = session["url"])

    if users.login(username, password):
        # Login successful
        if "url" in session:
            return redirect(session["url"])
        else:
            return redirect("/")
    else:
        # Login unsuccesful, provide the user an error message
        error = "Invalid username or password"
        return render_template("loginpage.html", error = error, prevURL = session["url"])


# Log out processing
@app.route("/logout")
def logout():
	
    users.logout()

    return redirect("/")


# Pages for different sections
@app.route("/section/<id>")
def section(id):
	# Set the session url in case the user is not yet logged in
    if not "username" in session:
        session["url"] = "/section/" + str(id)

    # Check if the user has access to the section
    hasAccess = users.check_section_access(id)
    # Check if the user is a moderator
    isModerator = users.is_moderator()

    sectionName = forum.get_section_name(id)
    isPrivate = forum.check_section_privacy(id)
    # Fetch the threads within the section
    threads = forum.list_threads(id)
	
    return render_template("section.html", id = id, threads = threads, sectionName = sectionName, isPrivate = isPrivate, isModerator = isModerator, hasAccess = hasAccess)

# Thread creation page
@app.route("/section/<id>/createthread")
def createthread(id):
	if not "username" in session:
        # User is not logged in, thread creation not possible
		hasAccess = False
	else:
        # Check if the user has access to the section
		hasAccess = users.check_section_access(id)
	
	return render_template("createthread.html", id = id, error = None, hasAccess = hasAccess)


# Posting the thread to the database
@app.route("/section/<id>/post_thread", methods = ["POST"])
def post_thread(id):

	# Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    threadTitle = request.form["threadTitle"]
    message = request.form["content"]

	# Make sure that a title and message is provided
    if not threadTitle or not message:
        error = "Please include both the thread and a message"
        return render_template("createthread.html", id = id, error = error, hasAccess = True)

    thread_id = forum.post_thread(threadTitle, message, id)

    return redirect("/section/" + str(id) + "/" + str(thread_id))


# Pages for different threads
@app.route("/section/<id>/<thread_id>")
def thread(id, thread_id):
	# Set the session url in case the user is not yet logged in
    if not "username" in session:
        session["url"] = "/section/" + str(id) + "/" + str(thread_id)

    hasAccess = users.check_section_access(id)
    isModerator = users.is_moderator()

    thread = forum.get_thread(thread_id)
    messages = forum.get_messages(thread_id)

    return render_template("thread.html", messages = messages, id = id, thread_id = thread_id, thread = thread, isModerator = isModerator, hasAccess = hasAccess)


# Page for writing a reply to a thread
@app.route("/section/<id>/<thread_id>/reply")
def reply(id, thread_id):
	if not "username" in session:
        # The user is not logged in, no permission to write replies
		hasAccess = False
	else:
        # Check that the user has access to the section
		hasAccess = users.check_section_access(id)

	return render_template("reply.html", id = id, thread_id = thread_id, error = None, hasAccess = hasAccess)


# Processing of the reply written to a thread
@app.route("/section/<id>/<thread_id>/post_reply", methods = ["POST"])
def post_reply(id, thread_id):

	# Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    content = request.form["content"]

	# Check that the reply is not empty
    if not content:
        error = "Empty replies are not allowed"
        return render_template("reply.html", id = id, thread_id = thread_id, error = error, hasAccess = True)	

    forum.post_message(content, thread_id)

    return redirect("/section/" + str(id) + "/" + str(thread_id))


# Editing a thread
@app.route("/section/<id>/<thread_id>/edit_thread")
def edit_thread(id, thread_id):
	
    if not "username" in session:
        # User is not logged in, no permission for thread editing
        hasAccess = False
    else:
        # First, check that the user has access to the section
        hasAccess = users.check_section_access(id)
        # Also check that the user is actually the creator of the thread
        isCreator = forum.check_if_thread_creator(thread_id)
        # Take the logical AND of these two conditions
        hasAccess = hasAccess and isCreator

    thread = forum.get_thread(thread_id)

    return render_template("editthread.html", id = id, thread_id = thread_id, thread = thread, error = None, hasAccess = hasAccess)


# Updating the thread database according to the edits
@app.route("/section/<id>/<thread_id>/post_thread_edit", methods = ["POST"])
def post_thread_edit(id, thread_id):

    # Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    thread_name = request.form["threadTitle"]
    content     = request.form["content"]

	# Check that a title and message are written
    if not thread_name or not content:
        error = "Please include both the thread title and message"
        thread = {"thread_name": thread_name, "content": content}
        return render_template("editthread.html", id = id, thread_id = thread_id, thread = thread, error = error, hasAccess = True)
	
    forum.post_thread_edit(thread_name, content, thread_id)

    return redirect("/section/" + str(id) + "/" + str(thread_id))


# Editing a message in a thread
@app.route("/section/<id>/<thread_id>/<message_id>/edit_message")
def edit_message(id, thread_id, message_id):

    if not "username" in session:
        # The user is not logged in, no permission to edit messages
        hasAccess = False
    else:
        # First, check that the user has access to the section
        hasAccess = users.check_section_access(id)
        # Also check that the user is the creator of the message
        isCreator = forum.check_if_message_creator(message_id)
        # Take the logical AND of these two conditions
        hasAccess = hasAccess and isCreator

    message = forum.get_message(message_id)

    return render_template("editmessage.html", id=id, thread_id = thread_id, message_id = message_id, message = message, error = None, hasAccess = hasAccess)


# Updating the message database according to the edits
@app.route("/section/<id>/<thread_id>/<message_id>/post_message_edit", methods = ["POST"])
def post_message_edit(id, thread_id, message_id):

	# Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    content = request.form["content"]

	# Check that something has been written
    if not content:
        error = "Please add a message"
        return render_template("editmessage.html", id = id, thread_id = thread_id, message_id = message_id, message = None, error = error, hasAccess = True)
	
    forum.post_message_edit(content, message_id)

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
	    
    if not "username" in session:
        # User not logged in, redirect to thread
        return redirect("/section/" + str(id) + "/" + str(thread_id))
    else:
        # If the user is the thread creator, delete the thread
        if forum.check_if_thread_creator(thread_id):
            forum.delete_thread(thread_id)

            return redirect("/section/" + str(id))
        else:
            # The user is not the creator, redirect to thread
            return redirect("/section/" + str(id) + "/" + str(thread_id))


# Processing of search results 
@app.route("/result", methods=["GET"])
def result():

    # Store the previous url to enable returning to it
    prevURL = request.args["prevURL"]

    # Set the query to lowercase to prevent case sensitivity
    query = request.args["query"].lower()

    messages, threads = forum.search_forum(query)

	# Render a page for the query results
    return render_template("result.html", messages = messages, threads = threads, prevURL = prevURL)

# Creation of sections
@app.route("/createsection")
def createsection():
    if not "username" in session:
        hasAccess = False
    else:
        # User with moderator status can create sections
        hasAccess = users.is_moderator()

    # Render the section creation page
    return render_template("createsection.html", error = None, hasAccess = hasAccess)

# Adding the section to the database table
@app.route("/post_section", methods=["POST"])
def post_section():

    # Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    section_name = request.form["sectionName"]

	# Check that a name is given for the section
    if not section_name:
        error = "Please input a name for the section"
        return render_template("createsection.html", error = error, hasAccess = True)

    # Create a boolean variable based on whether the checkbox "make private" is checked (True) or not (False)
    make_private = (len(request.form.getlist("makePrivate")) == 1)

    section_id = forum.create_section(section_name, make_private)

    # If the newly-created section is private, grant the creator access to it
    if make_private:
        users.grant_private_section_access(session["username"], section_id)

    return redirect("/")

# Deleting a section
@app.route("/deletesection/<section_id>")
def deletesection(section_id):

    if "username" in session:
        # Section can be deleted only by a moderator with access to the section
        if users.check_section_access(section_id) and users.is_moderator():
            forum.delete_section(section_id)
    return redirect("/")

# Granting a user moderator rights
@app.route("/promoteuser")
def promoteuser():

    if not "username" in session:
        return redirect("/")
    else:
        # The user has to be a moderator
        if users.is_moderator():
            return render_template("promoteuser.html", error = None)
        else:
            return redirect("/")
		

# Applying the promotion to the user table
@app.route("/applyPromotion", methods=["POST"])
def applyPromotion():

    # Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    username = request.form["username"]

	# Check that something is typed in
    if not username:
        error = "Please type in a username"
        return render_template("promoteuser.html", error = error)

    if users.promote_user(username):
        return redirect("/")
    else:
        error = "Username not found"
        return render_template("promoteuser.html", error = error)

# Page for granting a user access to a private section
@app.route("/<id>/grantuseraccess")
def grantuseraccess(id):
    
    if not "username" in session:
        hasAccess = False
    else:
        # The user needs to be a moderator and have access to the section
        hasAccess = users.check_section_access(id) and users.is_moderator()

    sectionName = forum.get_section_name(id)
	
    return render_template("grantuseraccess.html", id = id, section_name = sectionName, error = None, hasAccess = hasAccess)


# Applying the user access to the private section
@app.route("/<id>/applyuseraccess", methods=["POST"])
def applyuseraccess(id):

    # Prevent CRSF vulnerability exploitation
    if not users.crsf_token_valid(request.form["crsf_token"]):
        abort(403)

    username = request.form["username"]

	# Check that a valid username is typed in
    if not username or not users.is_existing_username(username):
        error = "Invalid username"
        sectionName = forum.get_section_name(id)
        
        return render_template("grantuseraccess.html", id = id, section_name = sectionName, error = error, hasAccess = True)

    users.grant_private_section_access(username, id)

    return redirect("/section/" + str(id))