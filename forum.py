from db import db

import users

from flask import session

# --- SECTIONS ---

def create_section(section_name, make_private):

    sql = "INSERT INTO sections (section_name, private) VALUES (:section_name, :make_private) RETURNING id"
    result = db.session.execute(sql, {"section_name": section_name, "make_private": make_private})
    section_id = result.fetchone().id

    return section_id

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

def get_section_name(id):
    # Query for the section name corresponding to the id
    sql = "SELECT section_name FROM sections WHERE id=:section_id"
    result = db.session.execute(sql, {"section_id": id})
    sectionName = result.fetchone().section_name
    return sectionName


def check_section_privacy(id):
    sql = "SELECT private FROM sections WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    isPrivate = result.fetchone().private

    return isPrivate


def delete_section(id):
    # Update the visible value of the deleted section to false 
    sql = "UPDATE sections SET visible=false WHERE id=:section_id"
    db.session.execute(sql, {"section_id": id})
    db.session.commit()


# --- THREADS ---


def list_threads(id):

    # Query for the thread id, posting time, thread name, and username of the poster for each thread
    sql = "SELECT T.id, T.posting_time, T.thread_name, U.username FROM threads T"\
    " LEFT JOIN users U ON T.user_id = U.id WHERE T.section_id=:id AND T.visible=true ORDER BY T.posting_time DESC"
    result = db.session.execute(sql, {"id": id})
    threads = result.fetchall()

    return threads


def get_thread(thread_id):

    # Query for the thread name and content
    sql = "SELECT T.thread_name, T.posting_time, T.content, U.username FROM threads T LEFT JOIN users U ON T.user_id = U.id WHERE T.id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id})
    thread = result.fetchone()

    return thread


def post_thread(threadTitle, message, id):

    user_id = users.get_user_id()

    # Insert thread into database
    sql = "INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), :user_id, :id, :threadTitle, :message) RETURNING id"
    result = db.session.execute(sql, {"user_id":user_id, "id":id, "threadTitle":threadTitle, "message":message})
    db.session.commit()
    thread_id = result.fetchone()[0]

    return thread_id

def post_thread_edit(thread_name, content, thread_id):

    # Update the thread database table accordingly
    sql = "UPDATE threads SET thread_name=:thread_name, content=:content WHERE id=:thread_id"
    db.session.execute(sql, {"thread_name":thread_name, "content":content, "thread_id":thread_id})
    db.session.commit()


def delete_thread(thread_id):

    sql = "UPDATE messages SET visible=false WHERE thread_id=:thread_id"
    db.session.execute(sql, {"thread_id":thread_id})
    db.session.commit()

    # Set the visibility of the thread to false
    sql = "UPDATE threads SET visible=false WHERE id=:thread_id"
    db.session.execute(sql, {"thread_id":thread_id})
    db.session.commit()

def check_if_thread_creator(thread_id):
    if not "username" in session:
        return False

    sql = "SELECT U.username FROM threads T LEFT JOIN users U on T.user_id = U.id WHERE T.id=:thread_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    user = result.fetchone().username

    isCreator = (user == session["username"])

    return isCreator

# --- MESSAGES ----

def get_messages(thread_id):

    # Query for the messages posted in the thread
    sql = "SELECT M.id, M.posting_time, M.content, U.username FROM messages M" \
    " LEFT JOIN users U ON U.id = M.user_id WHERE M.thread_id=:thread_id AND M.visible=true ORDER BY posting_time ASC"
    result = db.session.execute(sql, {"thread_id": thread_id})
    messages = result.fetchall()

    return messages

def get_message(message_id):

    # Query for the current content of the edited message
    sql = "SELECT content FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id": message_id})
    message = result.fetchone()

    return message


def post_message(content, thread_id):

    user_id = users.get_user_id()

    # Insert the reply into the database
    sql = "INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), :user_id, :thread_id, :content)"
    db.session.execute(sql, {"user_id": user_id, "thread_id": thread_id, "content": content})
    db.session.commit()


def post_message_edit(content, message_id):
    
    sql = "UPDATE messages SET content=:content WHERE id=:message_id"
    db.session.execute(sql, {"content":content, "message_id":message_id})
    db.session.commit()


def check_if_message_creator(message_id):
    if not "username" in session:
        return False

    sql = "SELECT U.username FROM messages M LEFT JOIN users U on M.user_id = U.id WHERE M.id=:message_id"
    result = db.session.execute(sql, {"message_id": message_id})
    user = result.fetchone().username

    isCreator = (user == session["username"])

    return isCreator


# --- QUERY ---

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




