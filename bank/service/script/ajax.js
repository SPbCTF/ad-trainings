
function getText(id){
	$.ajax({
		'url':'./index.php',
		'data': 'unfreeze_id='+id, 
		'type':'POST',
		'success':function(data){
			$('#unfreeze_data_'+id).html(data);	
		},
	});
	return getCash();
};

function getCash(){
	$.ajax({
		'url':'./index.php',
		'data': 'get_cash=please', 
		'type':'POST',
		'success':function(data){
			$('#cash').html(data);	
		},
	});
	return false;
}
