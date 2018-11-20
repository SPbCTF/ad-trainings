<?php

namespace app\modules\comments\actions;


use Yii;
use yii\base\Action;
use yii\web\HttpException;
use \yii\web\Response;

class ApiAction extends Action
{
    const ENV_WEB = 0;
    const ENV_APP = 1;

    public $env = self::ENV_WEB;
    public $ajaxOnly = false;
    public $jsonOnly = false;

    protected function beforeRun()
    {
        if(parent::beforeRun()){

            if($this->ajaxOnly){
                if(!(Yii::$app->request->isAjax || $this->env == self::ENV_APP))
                    throw new HttpException(405);
            }

            return true;
        }
        return false;
    }

    public function render($action, $data = NULL)
    {
        if(is_array($action) && $data === NULL) {
            $data = $action;
            $this->jsonOnly = true;
        }
        if(!$this->jsonOnly && $this->env == self::ENV_WEB) {
            return $this->ajaxOnly ? $this->controller->renderAjax($action, $data) :
                $this->controller->render($action, $data);
        }
        return $this->renderJSON($data);
    }

    protected function renderJSON($data)
    {
        Yii::$app->response->format = Response::FORMAT_JSON;
        return $data;
    }

}