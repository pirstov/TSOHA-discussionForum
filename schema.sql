/* This file includes the database schema */


/* Table for storing users */
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
INSERT INTO users (username, password) VALUES ('root', 'root');

/* Table for sections */
CREATE TABLE sections(id SERIAL PRIMARY KEY, section_name TEXT);
INSERT INTO sections (section_name) VALUES ('Nalle-osio');

/* Table for storing messages */
CREATE TABLE messages (id SERIAL PRIMARY KEY, posting_time TIMESTAMP, section_id INTEGER, content TEXT);
INSERT INTO messages (posting_time, section_id, content) VALUES (NOW(), 1, 'This is a message');
INSERT INTO messages (posting_time, section_id, content) VALUES (NOW(), 1, 'Another message!')