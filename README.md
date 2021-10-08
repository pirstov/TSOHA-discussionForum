# TSOHA-discussionForum
Repository for the database application course arranged by Helsinki University. The application is intended to provide a discussion forum, of which the theme is still under consideraiton.

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
Current status, as of 8th of October
---------------------------------------
Of the above requirements,
1. An initial implementation is complete.
2. An initial implementation is complete.
3. An initial implementation is complete.
4. An initial implementation is complete.
5. An initial implementation is complete.
6. TBD, not yet implemented
7. TBD, not yet implemented
8. TBD, not yet implemented.

First, basic forum functionality, such as browsing sections and threads, as well as account creation and logging in, is implemented. Following this, creation of threads and replies is to be implemented. In its wake/in parallel, use registration and log in functionality is to be further honed. Moderation rights, private discussions, modifications of threads/messages come in last.

To test this app in Heroku, enter the following in command line while accessing the project folder:
1. heroku login (log in with your credentials)
2. heroku apps:create (create an app, random name given)
3. heroku git:remote -a *APP NAME HERE*
4. heroku addons:create heroku-postgresql
5. heroku psql < schema.sql
6. heroku config:set SECRET_KEY=0a0be1a9ab88627f522663bce79ff46b
7. git push heroku main

This should yield succesful deployment of a Heroku webpage for the discussion forum.

Link to the Heroku app: http://tsoha-discussionforum.herokuapp.com/ (LAST UPDATED: 8th of October)

---------------------------------------