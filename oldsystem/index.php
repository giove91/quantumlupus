<?php

include_once "db_connection/config.php";
include_once "html_maker/generals.php";
include_once "html_maker/form.php";

start_html("QuantumLupus");

make_title("QuantumLupus - Il nuovo delirio");

connect();

// Controllo del settaggio della partita
$query = "SELECT * FROM ql_time";
$res = query($query);
if ( !($row = $res->fetch_assoc()) ) {
	// Partita non ancora settata
	paragraph("La partita non è stata ancora creata.");
	
	// Processo la registrazione
	$registered = FALSE;
	$user = "";
	$password = "";
	if ( isset($_POST["r_user"]) && isset($_POST["r_password"]) ) {
		$user = $GLOBALS["connection"]->real_escape_string($_POST["r_user"]);
		$password = $GLOBALS["connection"]->real_escape_string($_POST["r_password"]);
		if ( ( strlen($user) > 0 ) && ( strlen($password) > 0 ) && ( strlen($user) < 32 ) && ( strlen($password) < 256 ) ) {
			$query = "SELECT id FROM ql_players WHERE name='".$user."'";
			$res = query($query);
			if ( $res->fetch_assoc() ) {
				// Errore
				paragraph("Errore nella registrazione: nome già in uso.");
			}
			else {
				// Username disponibile
				// Scelta dell'id
				$query = "SELECT max(id) AS max FROM ql_players";
				$res = query($query);
				$row = $res->fetch_assoc();
				$max = $row["max"];
				if ( is_null($max) ) {
					$max = 0;
				}
				else $max = (int)$max;
				$id = $max+1;
				
				// Inserimento nel DB
				$query = "INSERT INTO ql_players VALUES (".$id.",'".$user."','".$password."',0)";
				$res = query($query);
				
				// Verifica
				$query = "SELECT id FROM ql_players WHERE (id=".$id.") AND (name='".$user."') AND (password='".$password."')";
				$res = query($query);
				if ( $row = $res->fetch_assoc() ) {
					$registered = TRUE;
					paragraph("Registrazione effettuata con successo (nome: ".$user."). Attendi l'inizio della partita.");
				}
				else {
					// Errore
					paragraph("Errore nella registrazione: qualcuno ti ha scippato l'id, riprova.");
				}
			}
		}
		else {
			// Errore
			paragraph("Errore nella registrazione: nome o password non sono della lunghezza appropriata.");
		}	
	}
	
	if ( !$registered ) {
		// Registrazione
		start_form("index.php","POST");
		paragraph(bold("Registrazione: ")."Username ".text_input("r_user",10,$user)." Password ".password_input("r_password",10,$password));
		paragraph(submit_input("Invia"));
		end_form();
	}
}
else {
	
	$phase = $row["phase"];
	$phase_text = "";
	$day = (int)($row["day"]);
	if ( $phase == 1 ) $phase_text = "Giorno";
	else $phase_text = "Notte";
	
	
	// Caricamento giocatori vivi
	// $query = "SELECT id, name FROM ql_players WHERE (death=0) ORDER BY name";
	$query = "SELECT id, name FROM ql_players ORDER BY name";
	$res = query($query);
	$players = array( array(0,"*Nessuno*") );
	while ( $row = $res->fetch_assoc() ) {
		$players[ $row["id"] ] = array( $row["id"], $row["name"] );
	}
	
	
	// Controllo del login
	$logged = FALSE;
	$user = "";
	$password = "";
	$player_id = NULL;
	if ( isset($_POST["user"]) && isset($_POST["password"]) ) {
		$user = $GLOBALS["connection"]->real_escape_string($_POST["user"]);
		$password = $GLOBALS["connection"]->real_escape_string($_POST["password"]);
		
		$query = "SELECT id FROM ql_players WHERE name='".$user."' AND password='".$password."'";
		$res = query($query);
		$row = $res->fetch_assoc();
		if ( $row ) {
			$logged = TRUE;
			$player_id = $row["id"];
		}
		else {
			paragraph("Le credenziali che hai inserito non sono valide.");
			$user = "";
			$password = "";
		}
	}
	if ( $logged ) paragraph("Sei stato riconosciuto come un giocatore valido, ".bold($user)." (id=".$player_id.").");
	
	$actions = array( 1 => "Vota", 2 => "Sbrana", 3 => "Scruta", 4 => "Proteggi" );
	
	// Processo le azioni
	if ( $logged ) {
		$types = array();
		
		if ( $phase == 1 ) {
			// Giorno
			$types = array(1);
		}
		else {
			// Notte
			$types = array(2,3,4);
		}
		
		foreach ( $types as $type ) {
			if ( isset($_POST["a".$type]) ) {
				$target = $_POST["a".$type];
				if ( is_numeric($target) ) {
					$target = (int)$target;
					if ( $target != 0 ) {
						if ( $target != 0 && array_key_exists($target,$players) && ($target != $player_id) ) {
							$query = "INSERT INTO ql_actions VALUES (0,".$player_id.", ".$type.", ".$target.", ".$day.")";
							//var_dump($query);
							$res = query($query);
							paragraph(bold("Notifica: ")."Memorizzata l'azione di tipo '".$actions[$type]."' su ".$players[$target][1]);
						}
						else paragraph(bold("Errore: ")."l'azione di tipo '".$actions[$type]."' su ".$players[$target][1]." non è stata ritenuta valida");
					}
				}
			}
		}
	}

	// Descrizione del tempo di gioco
	paragraph(bold("Tempo di gioco: ").$phase_text." ".$day);
	
	// Autenticazione
	start_form("index.php","POST");
	paragraph(bold("Autenticazione: ")."Username ".text_input("user",10,$user)." Password ".password_input("password",10,$password));
	
	
	
	// Azioni
	make_title("Azioni",2);
	
	$list = array();
	$tabella = array();
	if ( $phase == 	1 ) {
		// Giorno
		$tabella[] = array( "Votazione per la condanna a morte: ", select("a1",$players) );
	}
	else {
		// Notte
		$tabella[] = array( "Sbrana: ", select("a2",$players) );
		$tabella[] = array( "Scruta: ", select("a3",$players) );
		$tabella[] = array( "Proteggi: ", select("a4",$players) );
	}
	make_table($tabella);
	
	paragraph(submit_input("Invia"));
	
	end_form();
	
	// Status del villaggio
	make_title("Status del villaggio",2);
	
	// TODO: verificare che ogni giocatore compaia esattamente una volta
	$query = "SELECT p.id AS id, p.name AS name, p.death AS death, w.probability AS death_probability, w2.probability AS wolf_probability
		FROM ql_players AS p INNER JOIN ql_waves AS w ON (p.id=w.player_id)
		INNER JOIN ql_waves AS w2 ON (p.id=w2.player_id)
		WHERE (w.role_id=1) AND (w2.role_id=5) ORDER BY name";
	$res = query($query);
	$tabella = array();
	while ( $row = $res->fetch_assoc() ) {
		$status = "";
		if ( $row["death"] == 0 ) $status = "vivo con probabilità ".( (int)(100.0 - 100.0*$row["death_probability"])."%" );
		else $status = "morto mediamente il giorno ".sprintf("%.1lf",(double)($row["death"])/20.0);
		$role = "";
		if ( $row["death"] != 0 ) {
			if ( (double)($row["wolf_probability"]) > 0.9 ) $role = "(lupo)";
			else $role = "(villico)";
		}
		$tabella[] = array( $row["name"], $status, $role );
	}
	paragraph(return_table($tabella));
	
	
	// Log del villaggio
	make_title("Log del villaggio",2);
	
	$query = "SELECT * FROM ql_logs WHERE player_id=0 AND (day>=".($day-1).") ORDER BY day, id";
	$res = query($query);
	$list = array();
	while ( $row = $res->fetch_assoc() ) {
		$list[] = "[Giorno ".$row["day"]."] ".$row["content"];
	}
	make_list($list);
	
	
	// Status personale
	if ( $logged ) {
		make_title("Status personale",2);
		
		$query = "SELECT r.name AS role, w.probability AS probability
			FROM ql_waves AS w INNER JOIN ql_roles AS r ON (w.role_id=r.id) WHERE player_id=".$player_id." ORDER BY r.id";
		$res = query($query);
		$list = array();
		while ( $row = $res->fetch_assoc() ) {
			$list[] = $row["role"]." con probabilità ".((int)(100*((double)($row["probability"]))))."%";
		}
		make_list($list);
	}
	
	// Log personale
	if ( $logged ) {
		make_title("Log personale",2);
		
		$query = "SELECT * FROM ql_logs WHERE player_id=".$player_id." ORDER BY day DESC, id DESC";
		$res = query($query);
		$list = array();
		while ( $row = $res->fetch_assoc() ) {
			$list[] = "[Giorno ".$row["day"]."] ".$row["content"];
		}
		make_list($list);
	}
}

?>
