<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="language" content="en" />

	<!-- blueprint CSS framework -->
	<link rel="stylesheet" type="text/css" href="./css/css.css"/>
	<script src="./script/jquery-1.11.0.min.js"/></script>
	<script src="./script/ajax.js"/></script>
	
	<title><?php echo 'title'; ?></title>
</head>
<body>
<div id="page">
	<div id="header">
	</div>
	<div id="menu">
		<a href="./"><div class='menu_button'>Home</div></a>
		<?php if($user): ?>
		<a href="./?transactions=page"><div class='menu_button'>Transactions</div></a>
		<?php endif; ?>
		<?php if($user): ?>
		<a href="./?freeze=page"><div class='menu_button'>Frozen text</div></a>
		<?php endif; ?>
		<?php if($user): ?>
		<a href="./?logout=true"><div class='menu_button'>Logout</div></a>
		<?php elseif(true): ?>
		<a href="./?register=page"><div class='menu_button'>Registration</div></a>
		<?php endif; ?>
		<div id="info_user">
			<?php if(isset($user)):?>
			<table>
				<tr><td>Login:</td><td><?php echo $user['login']; ?></td></tr>
				<tr><td>Cash:</td><td id="cash"><?php echo $user['cash']; ?></td></tr>
			</table>
			<?php endif; ?>
		</div>
	</div>
	<div id="content">

