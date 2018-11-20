<?php
use yii\helpers\Html;
?>

<div id="comments">

    <?php if ($options['visible']): //if (Yii::$app->user->can('createComments')) : ?>
        <?= $this->render('_form', ['model' => $model, 'options'=>$options]); ?>
    <?php endif; ?>

    <?php
        echo $this->render('_index_item', ['models' => $models, 'options'=>[
            'answers' => $options['answers']
        ]]);
    ?>
    <!--/ #comments-list -->


</div>

<?php
//$js = "
//    $('.answer-activate').click(function(){
//        var pid = $(this).parents('.comment').attr('comment_id');
//        var div_form = $('#default-comment-form').clone();
//        var pid_input = '<input type=\"hidden\" name=\"". Html::getInputName($model, 'pid') .  "\" value=\"' + pid + '\">';
//
//        $('.answer-activate').show();
//        $('.other-comment-form').remove();
//        div_form.addClass('other-comment-form').find('form#{$model->formName()}').append(pid_input);
//        $(this).closest('.comment').children('.comment-info').after(div_form);
//        $(this).hide();
//        loadAjaxSubmit();
//    });
//";
$js = "
    $('.answer-activate.no-main').click(function(){
        var div_form = $('#default-comment-form');

        $('.answer-activate').show();
        $(div_form).show(400);
        $(this).closest('.comment').children('.comment-info').after(div_form);
        $(this).hide();

    });
";
$this->registerJs($js);
?>