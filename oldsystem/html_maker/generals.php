<?php



function start_html($titolo) {
	?>
		<html>
		<head>
			<meta charset='utf-8' />
			
			<title>
			<?php echo $titolo; ?>
			</title>
			<link rel="stylesheet" type="text/css" href="style.css" />
			
		</head>
		
		<body>
		
	<?php
	
}


function end_html() {
	?>
		</body>
		</html>
	<?php
}



function paragraph($frase) {
	echo "<p>".$frase."</p>";
}

function make_title($title, $dim=1) {
	echo "<h".$dim.">".$title."</h".$dim.">";
}

function return_table( $tabella, $style = FALSE, $head = FALSE, $chead = FALSE, $params = array("td" => "", "table" => "") ) {
	
	$result = "";
	
	$pt = "";
	if ( array_key_exists("table",$params) ) $pt = $params["table"];
	
	if ( $style ) $result .= "<table id=\"".$style."\" ".$pt.">";
	else $result .= "<table ".$pt.">";
	
	
	if ( array_key_exists("col_widths",$params) ) {
		foreach ( $params["col_widths"] as $width ) {
			$result .= "<col width=\"".$width."\">";
		}
	}
	
	if ( $head ) {
		$result .= "<thead>";
		foreach ( $head as $column ) {
			$result .= "<th>".$column."</th>";
		}
		$result .= "</thead><tbody>\n";
	}
	foreach ($tabella as $row) {
		$result.= "<tr>";
		$primo = TRUE;
		
		$par = NULL;
		if ( array_key_exists("td",$params) ) $par = $params["td"];
		else $par = "";
		
		foreach ($row as $column) {
			if ( $primo && $chead ) {
				$primo = FALSE;
				$result .= "<th ".$par.">".$column."</th>";
			}
			else $result .= "<td ".$par.">".$column."</td>";
		}
		$result .= "</tr>\n";
	}
	if ( $head ) $result .= "</tbody>";
	$result .= "</table>";
	
	return $result;
}

function make_table($tabella, $style = FALSE, $head = FALSE, $chead = FALSE, $params = array("td" => "", "table" => "") ) {
	echo return_table($tabella,$style,$head,$chead,$params);
}

function return_link ($pagina,$cosa) {
	return '<a href="'.$pagina.'">'.$cosa.'</a>';
}

function make_list ($list) {
	echo "<ul>";
	foreach ($list as $element) {
		echo "<li>".$element."</li>";
	}
	echo "</ul>";
}

function bold($text) {
	return "<b>".$text."</b>";
}

function italics($text) {
	return "<i>".$text."</i>";
}

?>
