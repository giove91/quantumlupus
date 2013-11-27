USE giove;

DROP TABLE IF EXISTS ql_players;
DROP TABLE IF EXISTS ql_roles;
DROP TABLE IF EXISTS ql_waves;
DROP TABLE IF EXISTS ql_actions;

-- PLAYERS

CREATE TABLE IF NOT EXISTS ql_players (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	password VARCHAR(256) NOT NULL,
	alive BOOL,
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
	PRIMARY KEY (id) );
