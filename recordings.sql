DROP TABLE IF EXISTS original;
DROP TABLE IF EXISTS recordings;

CREATE TABLE original(
id integer primary key autoincrement, 
rec_name varchar(50), 
rec_path text
);