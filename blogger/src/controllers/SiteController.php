<?php

namespace app\controllers;

use app\models\NoteForm;
use app\models\Page;
use Yii;
use yii\base\Exception;
use yii\filters\AccessControl;
use yii\web\Controller;
use yii\filters\VerbFilter;
use app\models\LoginForm;
use app\models\ContactForm;

class SiteController extends Controller
{
    public function behaviors()
    {
        return [
            'access' => [
                'class' => AccessControl::className(),
                'only' => ['logout'],
                'rules' => [
                    [
                        'actions' => ['logout'],
                        'allow' => true,
                        'roles' => ['@'],
                    ],
                ],
            ],
            'verbs' => [
                'class' => VerbFilter::className(),
                'actions' => [
                    'logout' => ['post'],
                ],
            ],
        ];
    }

    public function actions()
    {
        return [
            'error' => [
                'class' => 'yii\web\ErrorAction',
            ],
            'captcha' => [
                'class' => 'yii\captcha\CaptchaAction',
                'fixedVerifyCode' => YII_ENV_TEST ? 'testme' : null,
            ],
        ];
    }

    public function actionIndex()
    {
        $model = new Page();
        return $this->render('index', [
            'model'=>$model
        ]);
    }

    public function actionEnter()
    {
        $model = new Page();
        return $this->render('enter', [
            'model'=>$model
        ]);
    }

    public function actionNotes()
    {
        $models = [];

        $key = isset($_COOKIE['userid']) ? $_COOKIE['userid'] : false;
        if($key && ($data = Yii::$app->cache->get($key)) !== false){
            $models = json_decode($data);
        }

        $model = new NoteForm();
        if ($model->load(Yii::$app->request->post()) && $model->validate()) {
            $saveFile = [];
            if(($data = Yii::$app->cache->get($model->ident)) !== false){
                $saveFile = json_decode($data);
            }
            $saveFile[] = $model['txt'];
            Yii::$app->cache->set($model->ident, json_encode($saveFile));

            return $this->redirect(['/site/notes']);
        }
        $model->ident = $key;
        return $this->render('notes', [
            'model' => $model,
            'models' => $models
        ]);
    }

    public function actionAddNote()
    {

    }

    public function actionLoginadminchik()
    {
        if (!\Yii::$app->user->isGuest) {
            return $this->goHome();
        }

        $model = new LoginForm();
        if ($model->load(Yii::$app->request->post()) && $model->login()) {
            return $this->goBack();
        }
        return $this->render('login', [
            'model' => $model,
        ]);
    }

    public function actionLogout()
    {
        Yii::$app->user->logout();

        return $this->goHome();
    }

}
