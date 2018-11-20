<?php
$postfix = '_1';

$commishion = 500;

$T_users = 'users'.$postfix;
$T_frozen = 'frozen'.$postfix;
$T_transactions = 'transactions'.$postfix;

$ID_bank = 10000;

$pdo = new PDO(
	'mysql:host=localhost;dbname=lab_dbo_service', 
	'root',
	''
);

?>
