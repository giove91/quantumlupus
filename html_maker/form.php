<?php

function start_form($page,$method) {
	echo '<form action="'.$page.'" method="'.$method.'">';
}

function end_form() {
	echo '</form>';
}

function text_input($nome, $size = 30, $value = "", $params = "") {
	return '<input name="'.$nome.'" type="text" size="'.$size.'" value="'.$value.'" '.$params.' />';
}

function password_input($nome, $size = 30) {
	return '<input name="'.$nome.'" type="password" size="'.$size.'" value="" />';
}

function submit_input($value) {
	return '<input type="submit" value="'.$value.'" />';
}

function area($nome) {
	return '<textarea name="'.$nome.'" type="text" rows="5" cols="60"></textarea>';
}

function checkbox($name,$value = "1",$params="") {
	return '<input type="checkbox" name="'.$name.'" value="'.$value.'" '.$params.' />';
}

function select($name, $options, $params="") {
	$return = '<select name="'.$name.'" '.$params.'>';
	foreach ($options as $option) {
		$return .= '<option value="'.$option[0].'">'.$option[1].'</option>';
	}
	$return .= '</select>';
	
	return $return;
}

?>
