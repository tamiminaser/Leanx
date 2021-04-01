CREATE DATABASE leanx;

USE leanx;

CREATE TABLE login (
 id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(45) NOT NULL,
    email VARCHAR(45) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    salt VARCHAR(32) NOT NULL
);

CREATE TABLE profile (
	id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT NOT NULL,
	name varchar(45)  NOT NULL,
	email varchar(45) NOT NULL,
	profile_pic varchar(200) NOT NULL DEFAULT './img/no_pic.jpg', 
	occupation varchar(45) NULL, 
	location varchar(45) NULL
);

CREATE TABLE messages (
	id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT NOT NULL,
	message varchar(250),
	time_stamp timestamp DEFAULT CURRENT_TIMESTAMP
);
