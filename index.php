<?php

include_once "db_connection/config.php";
include_once "html_maker/generals.php";
include_once "html_maker/form.php";

start_html("QuantumLupus");

make_title("QuantumLupus - Il nuovo delirio");

$query = "SELECT * FROM ql_time";
$res = query($query);
if ( !($row = $res->fetch_assoc()) ) {
	// Partita non ancora settata
	
	
}


?>
