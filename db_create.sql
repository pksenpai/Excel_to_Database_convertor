CREATE DATABASE behrasam;

\c behrasam;

CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE reports(
	id SERIAL PRIMARY KEY,
	sender_id INTEGER NOT NULL,
	recipient_id INTEGER NOT NULL,
	FOREIGN KEY (sender_id) REFERENCES users(id),
	FOREIGN KEY (recipient_id) REFERENCES users(id)
);

/*
CREATE INDEX sender_idx ON
reports (sender_id);
CREATE INDEX recipient_idx ON
reports (recipient_id);
*/

