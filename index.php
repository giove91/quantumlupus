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
}
else {
	
	$phase = $row["phase"];
	$phase_text = "";
	$day = $row["day"];
	if ( $phase == 1 ) $phase_text = "Giorno";
	else $phase_text = "Notte";
	
	
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
	
	if ( $logged ) {
		// TODO: Processare le azioni
	}

	// Descrizione del tempo di gioco
	paragraph(bold("Tempo di gioco: ").$phase_text." ".$day);
	
	// Autenticazione
	start_form("index.php","POST");
	paragraph(bold("Autenticazione: ")."Username ".text_input("user",10,$user)." Password ".password_input("password",10,$password));
	
	// Caricamento giocatori vivi
	$query = "SELECT id, name FROM ql_players WHERE (death=0) ORDER BY name";
	$res = query($query);
	$players = array( array(0,"*Nessuno*") );
	while ( $row = $res->fetch_assoc() ) {
		$players[] = array( $row["id"], $row["name"] );
	}
	
	// Azioni
	make_title("Azioni",2);
	
	$list = array();
	if ( $phase == 	1 ) {
		// Giorno
		$list[] = "Votazione per la condanna a morte: ".select("1",$players);
	}
	else {
		// Notte
		$list[] = "Sbrana: ".select("2",$players);
		$list[] = "Scruta: ".select("3",$players);
		$list[] = "Proteggi: ".select("4",$players);
	}
	make_list($list);
	
	paragraph(submit_input("Invia"));
	
	end_form();
	
	// Informazioni note a tutti
	make_title("Status del villaggio",2);
	
	// TODO: cambiare la query in modo che ogni giocatore compaia solo una volta
	$query = "SELECT p.id AS id, p.name AS name, p.death AS death, r.name AS role
		FROM ql_players AS p LEFT JOIN ql_waves AS w ON (p.id=w.player_id) LEFT JOIN ql_roles AS r ON (w.role_id=r.id)
		WHERE (ISNULL(w.probability) OR (w.probability > 0.9)) AND (ISNULL(r.id) OR (r.id!=1)) ORDER BY name";
	$res = query($query);
	$tabella = array();
	while ( $row = $res->fetch_assoc() ) {
		$status = "";
		if ( $row["death"] == 0 ) $status = "Vivo";
		else $status = "Morto mediamente il giorno ".$row["death"];
		$role = "";
		if ( $row["death"] != 0 ) $role = $row["role"];
		$tabella[] = array( $row["name"], $status, $role );
	}
	paragraph(return_table($tabella));
	
	// Status personale
	if ( $logged ) {
		make_title("Status personale",2);
		
		$query = "SELECT r.name AS role, w.probability AS probability
			FROM ql_waves AS w INNER JOIN ql_roles AS r ON (w.role_id=r.id) WHERE player_id=".$player_id." ORDER BY r.id";
		$res = query($query);
		$list = array();
		while ( $row = $res->fetch_assoc() ) {
			$list[] = $row["role"]." con probabilità ".$row["probability"];
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
