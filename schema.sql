/* This file includes the database schema */


/* Table for storing users */
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
INSERT INTO users (username, password) VALUES ('root', 'root');

/* Table for sections */
CREATE TABLE sections(id SERIAL PRIMARY KEY, section_name TEXT);
/* Create an example for testing purposes */
INSERT INTO sections (section_name) VALUES ('Nalle-osio');

/* Table for threads within sections */
CREATE TABLE threads(id SERIAL PRIMARY KEY,  posting_time TIMESTAMP, section_id INTEGER, thread_name TEXT, content TEXT);
/* Create some examples for testing purposes */
INSERT INTO threads (posting_time, section_id, thread_name, content) VALUES (NOW(), 1, 'Is this really a thread?', 'This does not seem like a thread. More like a sequence of ones and zeroes.');
INSERT INTO threads (posting_time, section_id, thread_name, content) VALUES (NOW(), 1, 'How fluffly is Luna, exactly?', 'Luna seems like a fluffly madame. What do you reckon, is she hecka fluffly?');

/* Table for storing messages posted to threads within sections */
CREATE TABLE messages (id SERIAL PRIMARY KEY, posting_time TIMESTAMP, thread_id INTEGER, content TEXT);
/* Create some examples for testing purposes */
INSERT INTO messages (posting_time, thread_id, content) VALUES (NOW(), 1, 'This is a message');
INSERT INTO messages (posting_time, thread_id, content) VALUES (NOW(), 1, 'Another message!');
INSERT INTO messages (posting_time, thread_id, content) VALUES (NOW(), 2, 'WOW, new thread!');
INSERT INTO messages (posting_time, thread_id, content) VALUES (NOW(), 3, 'WOW, thread in another section!');