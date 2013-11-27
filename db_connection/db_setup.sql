USE giove;

DROP TABLE IF EXISTS ql_players;


-- PLAYERS

CREATE TABLE IF NOT EXISTS ql_players (
	id INT NOT NULL auto_increment,
	name VARCHAR(256) NOT NULL,
	PRIMARY KEY (id) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO ql_players VALUES
        (1, 'Tolkien'),
        (2, 'Rowling');


