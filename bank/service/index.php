<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

$views = "./views/";
include "config.php";
include "function.php";



$user = NULL;
$shield = NULL;
session_start(); 
if(isset($_GET['restart'])){
	restart($pdo);
	header("Location: ./");
}

if(isset($_POST['login'])){
	login($pdo, $_POST['login']);
}


if(isset($_GET['logout'])){
	session_destroy();
	header("Location: ./");
}

if(isset($_POST['on_register'])){
	if(!($_POST['password'] == $_POST['repeat_password'])){
		header("Location: ./?error=1");
		exit;
	}

	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE login=:login LIMIT 1');
	$q->execute(array(':login'=>$_POST['reg_login']));
	if($q->fetch()){
		header("Location: ./?error=2");
		exit;
	}
	$q = $pdo->prepare('INSERT INTO '.$T_users.' (login, password) VALUES (:login, :password)');
	$q->execute(array(':login'=>$_POST['reg_login'], ':password'=>$_POST['password']));
	header("Location: ./?reg_ok=1");
	exit;
}

if(isset($_GET['register'])){
	include "01.php";
	include $views."registration_form.php";
	include "02.php";
	exit;
}

if (isset($_SESSION['id_user'])){ 
	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE id=:id');
    $q->execute(array(':id'=>$_SESSION['id_user']));
	$user = $q->fetch();

	if(isset($_POST['get_cash'])){
		echo $user['cash'];
		exit;
	}

	if(isset($_POST['on_transaction'])){
		if($_POST['cash'] > $user['cash']){
			include "01.php";
			echo 'Need more cash!';
			include "02.php";
			exit;
		}
		send_money($pdo,$user);
		header("Location: ./?transactions=page");
	}

	if(isset($_POST['on_freeze'])){
		if( $commishion > $user['cash'] ){
			include "01.php";
			echo 'Need more cash!';
			include "02.php";
			exit;
		}
		$shield = freeze_text($pdo,$user);
	}
	
	if(isset($_POST['unfreeze_id'])){

        $q = $pdo->prepare('SELECT * FROM '.$T_frozen.' WHERE id=:id LIMIT 1');
        $q->execute(array(':id'=> $id ));
        $owner = $q->fetch()['owner'];

        $commishion = ($owner == $user['id'])?100:5000;
        var_dump($owner, $user);

		if( $commishion > $user['cash'] ){
			echo 'Need more cash!';
			exit;
		}
		echo unfreeze_text($pdo,$user,$_POST['unfreeze_id']);
		exit;
	}	

	include "01.php";
	if(isset($_GET['transactions'])){
		if($_GET['transactions'] == 'page'){
			echo "<h2>Transactions</h2>";
			print_transaction($pdo,$user);
		} 
		elseif($_GET['transactions'] == 'begin'){
			echo "<h2>Begin transactions</h2>";
			include $views."transactions_form.php";
		}
	}

	elseif(isset($_GET['freeze'])){
		if($_GET['freeze'] == 'page'){
			echo "<h2>Freeze text</h2>";
			print_frozen($pdo,$user);
		} 
		elseif($_GET['freeze'] == 'begin'){
			echo "<h2>Begin freeze</h2>";
			include $views."freeze_form.php";
		}
		
	}
	
	elseif($shield){
		echo "<h2>Your freeze shield:</h2>";
		echo ":::".$shield.":::<br>";
		echo "Remember ;)";
	}
 
	else {
		echo "<h2>Home page</h2>";
	}
	include "02.php";
	exit;
} 


elseif(isset($_GET['error'])) {
	include "01.php";
	if($_GET['error'] == 1) echo "<h2>Error in registration<br>Repeat password error</h2>";
	if($_GET['error'] == 2) echo "<h2>Error in registration<br>Change login</h2>";
	if($_GET['error'] == 3) echo "<h2>Error in registration<br>Too many users, <a href='./?restart=yes'>restart</a> please.</h2>";
	include "02.php";
	exit;
}

else{
	include "01.php";
	if(isset($_GET['reg_ok'])) echo "<h4>Registration succesful, login</h4>";
	include $views."login_form.php";
	include "02.php";
	exit;
}

?>
