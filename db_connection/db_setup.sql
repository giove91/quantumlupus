USE giove;

DROP TABLE IF EXISTS ql_players;
DROP TABLE IF EXISTS ql_roles;
DROP TABLE IF EXISTS ql_waves;
DROP TABLE IF EXISTS ql_actions;
DROP TABLE IF EXISTS ql_time;
DROP TABLE IF EXISTS ql_logs;
DROP TABLE IF EXISTS ql_game;

-- PLAYERS

CREATE TABLE IF NOT EXISTS ql_players (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	password VARCHAR(256) NOT NULL,
	death INT,
	PRIMARY KEY (id) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ROLES

CREATE TABLE IF NOT EXISTS ql_roles (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	PRIMARY KEY (id) );


-- WAVES

CREATE TABLE IF NOT EXISTS ql_waves (
	id INT NOT NULL auto_increment,
	player_id INT NOT NULL,
	role_id INT NOT NULL,
	probability DOUBLE,
	PRIMARY KEY (id) );

-- ACTIONS

CREATE TABLE IF NOT EXISTS ql_actions (
	id INT NOT NULL auto_increment,
	player_id INT NOT NULL,
	type INT NOT NULL,
	target_id INT NOT NULL,
	day INT NOT NULL,
	PRIMARY KEY (id) );

-- TIME

CREATE TABLE IF NOT EXISTS ql_time (
	day INT NOT NULL,
	phase INT NOT NULL );


-- LOGS

CREATE TABLE IF NOT EXISTS ql_logs (
	id INT NOT NULL auto_increment,
	player_id INT NOT NULL,
	day INT NOT NULL,
	content VARCHAR(256),
	PRIMARY KEY (id) );


-- GAME

CREATE TABLE IF NOT EXISTS ql_game (
	role_id INT NOT NULL,
	num INT,
	PRIMARY KEY (role_id) );
