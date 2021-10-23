# TSOHA-discussionForum
Repository for the database application course arranged by University of Helsinki. The application is intended to provide a discussion forum, of which the theme is still under consideraiton.

The target is to implement at least the properties listed below.
1. The user can create an account and log in.
2. The used can see the list of the different discussion areas for each subtopic related to the theme of the forum. In addition, the number of messages and threads can be seen for each subtopic, as well as the timestamp for the most recent post.
3. The user can create new threads by giving the thread a title and the content of the starting message.
4. The user can reply to existing threads.
5. The user can modify the title of their own threads, as well as the content of their own messages. Own threads and messages can also be deleted.
6. The user can search the discussion forum for messages that include the word they searched for.
7. Users may have moderation rights, which enables them to add and delete separate discussion areas to the forum.
8. The user with moderation rights can create a private discussion area and define, which users have access to it.

---------------------------------------
Current status, as of 10th of October
---------------------------------------
Of the above requirements,
1. Implemented. 
2. Implemented. Although, the structure of thread table is subject to modification so that the message content is placed in the messages table.
3. Implemented.
4. Implemented.
5. Implemented.
6. Implemented. Should the structure of thread table be subject to modification, this it to be modified accordingly.
7. Implemented.
8. Implemented.

Next steps include, but are not limited to:
- Considering the modification of thread table
- Splitting the "app.py" into modules for messages, threads, sections, registration/login etc
- Improving the interactivity of the forum by adding more messages for the user related to succesful logins, account/thead/message creations
- Improving the layout of the pages
- Implementing the calculation of number of replies in each thread for the section view
- Going over the accessibility of each page, so for example a user that is not logged in can not go to message creation page


To test this app in Heroku, enter the following in command line while accessing the project folder:
1. heroku login (log in with your credentials)
2. heroku apps:create (create an app, random name given)
3. heroku git:remote -a *APP NAME HERE*
4. heroku addons:create heroku-postgresql
5. heroku psql < schema.sql
6. heroku config:set SECRET_KEY=<INSERT THE DESIRED SECRET KEY HERE>
7. git push heroku main

This should yield succesful deployment of a Heroku webpage for the discussion forum.

Link to the Heroku app: http://tsoha-discussionforum.herokuapp.com/ (LAST UPDATED: 10th of October)

PRE-MADE ACCOUNTS FOR TESTING:
user: root / password: root (moderator account)
user: tester / password: 123

----------------------------------