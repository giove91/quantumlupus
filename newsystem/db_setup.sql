-- ____CONSTANTS_____
--
-- DAY_NONE			0
-- PHASE_DAY		1
-- PHASE_NIGHT		2
--
-- STATUS_ROLE		1
-- STATUS_WOLFRIEND	2
-- STATUS_DEATHDAY	3
--
-- ROLE_DEAD		0
-- ROLE_COMMONER	1	// associated action: vote
-- ROLE_SEER		2
-- ROLE_PHYSICIAN	3
-- ROLE_STALKER		4
-- ROLE_WATCHMAN	5
-- ROLE_PRIEST		6	// the target is measured villager (if this is not possible, the priest dies)
-- ROLE_REVIVER		7	// the target is measured alive (if this is not possible, the reviver dies)
-- ROLE_SHAMAN		8
-- ROLE_HUNTER		9
-- ROLE_GUARD		10
-- ROLE_MAYOR		11
-- ROLE_LOVER		12
-- ROLE_WEREWOLF	13
-- -------------------


DROP DATABASE IF EXISTS quantum_werewolves;
CREATE DATABASE quantum_werewolves;
USE quantum_werewolves;

-- GAMES

CREATE TABLE games (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	password VARCHAR(256),
	admin_id INT NOT NULL,
	day INT NOT NULL DEFAULT 0,
	phase INT NOT NULL DEFAULT 1,
	countdown INT,
	limit_day INT,
	limit_night INT,
	max_players INT,
	max_states INT,
	tie_draw BOOL NOT NULL DEFAULT FALSE,
	tie_play_off BOOL NOT NULL DEFAULT FALSE,
	tie_conclave BOOL NOT NULL DEFAULT FALSE,
	PRIMARY KEY (id)
	) DEFAULT CHARSET=utf8;


-- PLAYERS

CREATE TABLE players (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	password VARCHAR(256) NOT NULL,
	game_id INT,
	PRIMARY KEY (id)
	) DEFAULT CHARSET=utf8;


-- VILLAGES

CREATE TABLE villages (
	game_id INT NOT NULL,
	role_id INT NOT NULL,
	is_quantum BOOL NOT NULL DEFAULT FALSE,
	num INT NOT NULL DEFAULT 1,
	PRIMARY KEY (game_id)
	);


-- STATUS

CREATE TABLE status (
	player_id INT NOT NULL,
	status_type INT NOT NULL,
	value_id INT NOT NULL,
	probability DOUBLE NOT NULL,
	PRIMARY KEY (player_id)
	);


-- ACTIONS

CREATE TABLE actions (
	id INT NOT NULL auto_increment,
	day INT NOT NULL,
	player_id INT NOT NULL,
	role_id INT NOT NULL,
	target_id INT NOT NULL,
	PRIMARY KEY (id)
	);


-- LOGS

CREATE TABLE logs (
	id INT NOT NULL auto_increment,
	day INT NOT NULL,
	player_id INT NOT NULL,
	content VARCHAR(256) NOT NULL,
	PRIMARY KEY (id)
	) DEFAULT CHARSET=utf8;
