<?php

namespace app\modules\comments\controllers;

use app\modules\comments\actions\CommentCreateAction;
use Yii;
use yii\web\Controller;


class DefaultController extends Controller
{

    public function actions()
    {
        return [
            'create' => [
                'class' => CommentCreateAction::className(),
            ],

        ];
    }

}
