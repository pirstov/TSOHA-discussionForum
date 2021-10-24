from db import db

import users

from flask import session

# --- SECTIONS ---

# Create a section with the name and privacy according to its arguments
def create_section(section_name, make_private):

    sql = "INSERT INTO sections (section_name, private) VALUES (:section_name, :make_private) RETURNING id"
    result = db.session.execute(sql, {"section_name": section_name, "make_private": make_private})
    section_id = result.fetchone().id

    return section_id


# Form a list of sections based on the user rights
def list_sections():

    if "username" in session:
        # User is logged in, check which private sections are accessible
        user_id = users.get_user_id()
		# Query for the sections that are not private or private to which the user has privilege
        sql = "SELECT S.id, S.section_name, S.private, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
            " max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
            "LEFT JOIN messages M on T.id = M.thread_id WHERE S.visible=true "\
            "GROUP BY S.id HAVING (NOT S.private OR S.id IN (SELECT section_id FROM user_privileges WHERE user_id=:user_id))"
        result = db.session.execute(sql, {"user_id":user_id})
    else:
		# The user is not logged in, fetch sections that are not private
        result = db.session.execute("SELECT S.id, S.section_name, S.private, count(DISTINCT T.id) AS thread_count, count(M.id) AS message_count, " \
        " max(M.posting_time) FROM sections S LEFT JOIN threads T ON S.id = T.section_id " \
        "LEFT JOIN messages M on T.id = M.thread_id WHERE S.visible=true AND S.private=false GROUP BY S.id")
    sections = result.fetchall()

    return sections


# Query for the section name corresponding to the id
def get_section_name(id):
    
    sql = "SELECT section_name FROM sections WHERE id=:section_id"
    result = db.session.execute(sql, {"section_id": id})
    sectionName = result.fetchone().section_name

    return sectionName


# Check whether a section is private
def check_section_privacy(id):

    sql = "SELECT private FROM sections WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    isPrivate = result.fetchone().private

    return isPrivate

# Delete a section
def delete_section(id):

    sql = "UPDATE sections SET visible=false WHERE id=:section_id"
    db.session.execute(sql, {"section_id": id})
    db.session.commit()


# --- THREADS ---

# Query for the relevant columns of threads in the argument section
def list_threads(id):

    sql = "SELECT T.id, T.posting_time, T.thread_name, U.username, COUNT(M.id) AS reply_count FROM users U LEFT JOIN threads T"\
    " ON T.user_id = U.id LEFT JOIN messages M ON T.id = M.thread_id WHERE T.section_id=:id AND T.visible=true "\
    " GROUP BY (T.id, U.username) ORDER BY T.posting_time DESC"
    result = db.session.execute(sql, {"id": id})
    threads = result.fetchall()

    return threads


# Query for the relevant columns of a thread given as an argument
def get_thread(thread_id):

    sql = "SELECT T.thread_name, T.posting_time, T.content, U.username FROM threads T LEFT JOIN users U ON T.user_id = U.id WHERE T.id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id})
    thread = result.fetchone()

    return thread


# Add a thread with a title, message and section identifier according to the arguments
def post_thread(threadTitle, message, id):

    user_id = users.get_user_id()

    sql = "INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), :user_id, :id, :threadTitle, :message) RETURNING id"
    result = db.session.execute(sql, {"user_id":user_id, "id":id, "threadTitle":threadTitle, "message":message})
    db.session.commit()
    thread_id = result.fetchone()[0]

    return thread_id


# Update a thread given as an argument with the title and content given as arguments 
def post_thread_edit(thread_name, content, thread_id):

    sql = "UPDATE threads SET thread_name=:thread_name, content=:content WHERE id=:thread_id"
    db.session.execute(sql, {"thread_name":thread_name, "content":content, "thread_id":thread_id})
    db.session.commit()


# Delete the thread given as an argument
def delete_thread(thread_id):

    sql = "UPDATE messages SET visible=false WHERE thread_id=:thread_id"
    db.session.execute(sql, {"thread_id":thread_id})
    db.session.commit()

    # Set the visibility of the thread to false
    sql = "UPDATE threads SET visible=false WHERE id=:thread_id"
    db.session.execute(sql, {"thread_id":thread_id})
    db.session.commit()


# Check if the user is the creator of the thread given as the argument
def check_if_thread_creator(thread_id):
    if not "username" in session:
        return False

    sql = "SELECT U.username FROM threads T LEFT JOIN users U on T.user_id = U.id WHERE T.id=:thread_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    user = result.fetchone().username

    isCreator = (user == session["username"])

    return isCreator

# --- MESSAGES ----

# Fetch relevant information related to messages in the thread given as an argument
def get_messages(thread_id):

    # Query for the messages posted in the thread
    sql = "SELECT M.id, M.posting_time, M.content, U.username FROM messages M" \
    " LEFT JOIN users U ON U.id = M.user_id WHERE M.thread_id=:thread_id AND M.visible=true ORDER BY posting_time ASC"
    result = db.session.execute(sql, {"thread_id": thread_id})
    messages = result.fetchall()

    return messages

# Fetch the content of the message given as an argument
def get_message(message_id):

    # Query for the current content of the edited message
    sql = "SELECT content FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id": message_id})
    message = result.fetchone()

    return message


# Add a message with content and thread identifier given by the argument to the database
def post_message(content, thread_id):

    user_id = users.get_user_id()

    # Insert the reply into the database
    sql = "INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), :user_id, :thread_id, :content)"
    db.session.execute(sql, {"user_id": user_id, "thread_id": thread_id, "content": content})
    db.session.commit()


# Update a message given as an argument with the content given as another argument
def post_message_edit(content, message_id):
    
    sql = "UPDATE messages SET content=:content WHERE id=:message_id"
    db.session.execute(sql, {"content":content, "message_id":message_id})
    db.session.commit()

# Delete the message given as an argument
def delete_message(message_id):

    sql = "UPDATE messages SET visible=false WHERE id=:message_id"
    db.session.execute(sql, {"message_id": message_id})
    db.session.commit()

# Check if the user is the creator of the message given as an argument
def check_if_message_creator(message_id):
    if not "username" in session:
        return False

    sql = "SELECT U.username FROM messages M LEFT JOIN users U on M.user_id = U.id WHERE M.id=:message_id"
    result = db.session.execute(sql, {"message_id": message_id})
    user = result.fetchone().username

    isCreator = (user == session["username"])

    return isCreator


# --- QUERY ---

# Fetch the threads and messages with the queried string in them
def search_forum(query):

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

    return messages, threads




