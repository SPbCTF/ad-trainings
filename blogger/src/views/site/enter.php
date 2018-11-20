<?php

    use yii\helpers\Html;
    use yii\widgets\ActiveForm;

    $this->title = 'Enter';

    if (isset($_COOKIE['userid'])) {
        unset($_COOKIE['userid']);
        setcookie('userid', null, -1, '/');
    }

?>
<div class="note-form">
    <h1>Input your identifier</h1>
    <input id="identifier" type="text" onkeydown="setCookie()">
</div>


<script language="javascript">

    function setCookie() {
        if(event.keyCode == 13) {
            var d = new Date();
            d.setTime(d.getTime() + (1 * 24 * 60 * 60 * 1000));
            var expires = "expires=" + d.toUTCString();
            document.cookie = "userid=" + document.getElementById('identifier').value + ";" + expires + ";path=/";
            window.location = '/';
        }
    }
</script>