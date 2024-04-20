DROP TABLE IF EXISTS original;
DROP TABLE IF EXISTS recordings;

CREATE TABLE original(
id integer primary key autoincrement, 
rec_name varchar(50), 
rec_path text
);

CREATE TABLE edited(
id INTEGER PRIMARY KEY AUTOINCREMENT, 
flag INTEGER, 
edit_name varchar(50), 
edit_path TEXT, 
speed REAL
);
