<?php
function restart($pdo)
{
	global $T_users,$T_transactions,$T_frozen;
	$pdo->query('TRUNCATE TABLE '.$T_users);
	$pdo->query('TRUNCATE TABLE '.$T_transactions);
	$pdo->query('TRUNCATE TABLE '.$T_frozen);
	$pdo->query('INSERT INTO '.$T_users.' (id,login,password,cash) VALUES (10000,"admin","Pa$$w0rD",10000)');
	session_destroy();
}

function login($pdo,$login)
{
	global $T_users,$T_transactions;
	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE login=:login LIMIT 1');
	$q->execute(array(':login'=>$login));
	$row = $q->fetch();
	if (is_array($row)){
		if ($row['password'] == $_POST['password'])
			$_SESSION['id_user'] = $row['id'];
	}
}
function send_money($pdo,$user)
{
	global $T_users,$T_transactions;
	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE id=:id LIMIT 1');
	$q->execute(array(':id'=>$_POST['id_receiver']));
	$receiver = $q->fetch();
	if($receiver){
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash+:cash WHERE id=:id_receiver LIMIT 1');
		$q->execute(array(':cash'=>$_POST['cash'], ':id_receiver'=>$_POST['id_receiver']));
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash-:cash WHERE id=:id_sender LIMIT 1');
		$q->execute(array(':cash'=>$_POST['cash'], ':id_sender'=>$user['id']));
		$q = $pdo->prepare('INSERT INTO '.$T_transactions.' (id_sender, id_receiver, cash) VALUES (:id_sender, :id_receiver, :cash)');
		$q->execute(array(':id_sender'=>$user['id'],':id_receiver'=>$_POST['id_receiver'],':cash'=>$_POST['cash'])); 
	}
}

function freeze_text($pdo,$user)
{
	global $T_users,$T_transactions,$T_frozen,$commishion,$ID_bank;
	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE id=:id LIMIT 1');
	$q->execute(array(':id'=> $ID_bank ));
	$receiver = $q->fetch();
	if($receiver){
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash+:cash WHERE id=:id_receiver LIMIT 1');
		$q->execute(array(':cash'=>$commishion, ':id_receiver'=>$ID_bank));
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash-:cash WHERE id=:id_sender LIMIT 1');
		$q->execute(array(':cash'=>$commishion, ':id_sender'=>$user['id']));
		
		$q = $pdo->prepare('INSERT INTO '.$T_transactions.' (id_sender, id_receiver, cash) VALUES (:id_sender, :id_receiver, :cash)');
		$q->execute(array(':id_sender'=>$user['id'],':id_receiver'=>$ID_bank,':cash'=>$commishion));
		
		$q = $pdo->prepare('INSERT INTO '.$T_frozen.' (text, shield) VALUES (:text, :shield)');
		$q->execute(array(
			':text'=>$_POST['text'],
			':shield'=> $shield = random_gen(10) 
		));
		return $shield;
	}
}

function unfreeze_text($pdo,$user,$id)
{
	global $T_users,$T_transactions,$T_frozen,$commishion, $ID_bank;
	$q = $pdo->prepare('SELECT * FROM '.$T_users.' WHERE id=:id LIMIT 1');
	$q->execute(array(':id'=> $ID_bank ));
	$receiver = $q->fetch();

	if ($receiver['id'] == $user['id']) {
        $commishion = 500;
	}

	if($receiver){
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash+:cash WHERE id=:id_receiver LIMIT 1');
		$q->execute(array(':cash'=>$commishion, ':id_receiver'=>$ID_bank));
		$q = $pdo->prepare('UPDATE '.$T_users.' SET cash=cash-:cash WHERE id=:id_sender LIMIT 1');
		$q->execute(array(':cash'=>$commishion, ':id_sender'=>$user['id']));
		$q = $pdo->prepare('INSERT INTO '.$T_transactions.' (id_sender, id_receiver, cash) VALUES (:id_sender, :id_receiver, :cash)');
		$q->execute(array(':id_sender'=>$user['id'],':id_receiver'=>$ID_bank,':cash'=>$commishion));
		$q = $pdo->prepare('SELECT text FROM '.$T_frozen.' WHERE id=:id');
		$q->execute(array(':id'=>$id));
		if($res = $q->fetch())	
			return $res['text'];
		else
			return "Error, sorry";
	}
}

function print_transaction($pdo,$user)
{
	global $T_users,$T_transactions;
	echo '<a href="./?transactions=begin"><div id="begin_tran">Begin transactions</div></a><br>';
	$q = $pdo->prepare('SELECT * FROM '.$T_transactions.' WHERE id_sender=:id ORDER BY datatime DESC');
	$q->execute(array(':id'=>$user['id']));
	$row = $q->fetch();
	if(!$row)
		echo "Empty";
	else {
		echo "<table width=50% border=1>";
		echo "<tr><td width=20%>Receiver</td><td width=40%>Cash</td><td width=60%>Data</td></tr>";
		echo "<tr><td>".$row['id_receiver']."</td><td>".$row['cash']."</td><td>".$row['datatime']."</td></tr>";
		while($row = $q->fetch())
			echo "<tr><td>".$row['id_receiver']."</td><td>".$row['cash']."</td><td>".$row['datatime']."</td></tr>";
		echo "</table>";
	}
}

function print_frozen($pdo,$user)
{
	global $T_users,$T_frozen;
	echo '<a href="./?freeze=begin"><div id="begin_tran">Begin freeze</div></a><br>';
	$q = $pdo->prepare('SELECT * FROM '.$T_frozen.' ORDER BY datatime DESC');
	$q->execute();
	echo "Unfreeze shield cost 500$";
	echo "<table width=50% border=1>";
	echo "<tr><td width=20%>ID</td><td width=40%>Shield</td><td width=60%>Data</td></tr>";
	
	while($row = $q->fetch())
		echo 	"<tr>
				<td>".$row['id']."</td>
				<td class='shield' onclick='getText(".$row['id'].");'>".
						$row['shield'].	
				"</td>
				<td>".
					"<div id='unfreeze_data_".$row['id']."'></div>".
				"</td>
			</tr>";
	echo "</table>";
	
}

function random_gen($count = 8)
{
	$base = 'qwertyuioasdfghjklpzxcvbnm1234567890';
	$str = '';
	for($i = 0; $i < $count; $i++)
		$str .= $base[rand(0,strlen($base)-1)];
	return $str;
}
?>
