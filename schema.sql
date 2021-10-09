/* This file includes the database schema */


/* Table for storing users */
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT, moderator BOOLEAN DEFAULT false);
INSERT INTO users (username, password, moderator) VALUES ('root', 'root', true);
INSERT INTO users (username, password) VALUES ('tester', '123');

/* Table for sections */
CREATE TABLE sections(id SERIAL PRIMARY KEY, section_name TEXT, visible BOOLEAN DEFAULT true);
/* Create an example for testing purposes */
INSERT INTO sections (section_name) VALUES ('Nalle-osio');

/* Table for threads within sections */
CREATE TABLE threads(id SERIAL PRIMARY KEY,  posting_time TIMESTAMP, user_id INTEGER REFERENCES users, section_id INTEGER REFERENCES sections, thread_name TEXT, content TEXT, visible BOOLEAN DEFAULT true);
/* Create some examples for testing purposes */
INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), 1, 1, 'Is this really a thread?', 'This does not seem like a thread. More like a sequence of ones and zeroes.');
INSERT INTO threads (posting_time, user_id, section_id, thread_name, content) VALUES (NOW(), 2, 1, 'How fluffy is Luna, exactly?', 'Luna seems like a fluffy madame. What do you reckon, is she hecka fluffy?');

/* Table for storing messages posted to threads within sections */
CREATE TABLE messages (id SERIAL PRIMARY KEY, posting_time TIMESTAMP, user_id INTEGER REFERENCES users, thread_id INTEGER REFERENCES threads, content TEXT, visible BOOLEAN DEFAULT true);
/* Create some examples for testing purposes */
INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), 1, 1, 'This is a message');
INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), 2, 1, 'Another message!');
INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), 2, 2, 'WOW, new thread!');
INSERT INTO messages (posting_time, user_id, thread_id, content) VALUES (NOW(), 1, 2, 'WOW, thread in another section!');