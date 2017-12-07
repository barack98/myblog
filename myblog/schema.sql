drop table if exists entries;
CREATE TABLE entries (
	id integer PRIMARY KEY autoincrement,
	title text NOT NULL,
	'text' text NOT NULL
);