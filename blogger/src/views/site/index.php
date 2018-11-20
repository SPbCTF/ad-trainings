<?php

/* @var $this yii\web\View */

    use app\modules\comments\widgets\CommentsWidget;

    $this->title = 'My Yii Application';
?>
<div class="site-index">

    <div class="jumbotron">
        <h1>Hello stranger!</h1>
    </div>

    <div class="body-content" style="border: 1px solid #aaa;">

        <div class="row">
            <div class="col-md-12">
                <h1 class="text-center">
                    <?=$model->title?>
                </h1>
                <p>
                    <?=$model->description?>
                </p>

                <?php echo CommentsWidget::widget([
                    'model' => $model,
                    'options' => [
                        'upload' => false,
                    ]
                ]); ?>

            </div>
        </div>

    </div>
</div>
