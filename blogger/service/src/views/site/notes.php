<?php

    use yii\helpers\Html;
    use yii\widgets\ActiveForm;

    $this->title = 'Notes';

?>
<div class="note-form">
    <?php $form = ActiveForm::begin([
        'enableClientValidation'=>false,
        'id' => 'note-form',
        'options' => ['class' => 'form-horizontal'],
        'fieldConfig' => [
            'template' => "<div class=\"col-md-12\">{label}</div><div class=\"col-md-8\">{input}</div><div class=\"col-md-4\">{error}</div>",
            'labelOptions' => ['class' => 'col-lg-1 control-label'],
        ],
    ]); ?>
        <?= $form->field($model, 'txt')->textArea() ?>
        <?= $form->field($model, 'ident', ['template'=>'{input}'])->hiddenInput(['value' => isset($_COOKIE['userid'])?$_COOKIE['userid']:'']) ?>

        <div class="form-group">
            <div class="col-lg-offset-1 col-lg-11">
                <?= Html::submitButton('Отправить', ['class' => 'btn btn-primary', 'name' => 'notes-button']) ?>
            </div>
        </div>

    <?php ActiveForm::end(); ?>
</div>

<?php
    if(count($models)){
        echo 'Your notes<br>:';
        echo implode('<br>:', $models);
    }
    else {
        echo 'Notes list is empty';
    }
?>