<?php

use yii\helpers\Html;
use yii\helpers\Url;
use yii\widgets\ActiveForm;


$js = "
    function loadAjaxSubmit(){
        $('form#{$model->formName()}').on('submit', function(e) {
            e.preventDefault();
            var form = $(this);
            $('#" . Html::getInputId($model, 'txt') . "').parent().removeClass('has-error');

            $.ajax({
                url: '".Url::to(['/comments/default/create'])."',
                type: 'POST',
                data: form.serializeArray(),
                dataType: 'json',
                success: function (data) {
                    if(! data.message ){
                        alert('Epic error.');
                        return;
                    }
                    if( data.message == 'success' ){

                        $(form).find('#comments-txt').val('');

                        var div_form = $(form).parents('#default-comment-form');
                        $(div_form).hide(400);
                        if($(div_form).next().hasClass('c-responce'))
                            $(div_form).next().html('<div class=\"answers\">' + data.html + '</div>');
                        else
                            $(div_form).after(data.html);
                    } else if(data.message == 'error'){
                        $('#" . Html::getInputId($model, 'txt') . "').parent().addClass('has-error');
                    }
                }
            });

            return false;
        });
    }
    loadAjaxSubmit();
";
$this->registerJs($js);
$js = "
    $('.answer-activate.main').click(function(){
        var div_form = $('#default-comment-form');

        $('.answer-activate').show();

        $(this).after(div_form);
        $(div_form).show(400);
        $(this).hide();
    });
";
$this->registerJs($js);
?>


<span class="answer-activate main btn" style="display: none; clear: both; float: none; margin-bottom: 10px">Answer</span>
<div id="default-comment-form" class="comment-form">
    <div class="c-avatar" style="background-image: url(<?php //echo Yii::$app->user->identity->photo ;?>)"></div>
    <div class="c-leave">
        <div id="add-status" class="add-status"></div>
        <?php
            $form = ActiveForm::begin([
                'id'=> $model->formName(),
                'method' => 'POST',
                'action' => Url::to(['/comments/default/create']),
                'options' => ['class'=>'add-comment'],
                'fieldConfig' => [
                    'template' => '{input}{error}',
                ],
                'enableClientScript' => false
            ]);
        ?>
        <?php echo $form->field($model, 'txt')->textarea([
                'class'=>"comment-leave",
                'placeholder'=>"Comment"
            ]); ?>

        <?php echo Html::submitButton('Send', [
            'id' => 'send-button',
            'class' => 'btn btn-primary',
        ]) ; ?>

        <?php ActiveForm::end(); ?>
    </div>
    <div style="clear:both;"></div>
</div>