<?php

namespace app\modules\comments\widgets;

use Yii;
use yii\base\InvalidConfigException;
use yii\base\Widget;

use app\modules\comments\models\Comments;

class CommentsWidget extends Widget
{
    /**
     * @var \yii\db\ActiveRecord|null Widget model
     */
    public $model;

    /**
     * @var array Comments Javascript plugin options
     */
    public $options = [];

    /**
     * @inheritdoc
     */
    public function init()
    {
        parent::init();

        if ($this->model === null) {
            throw new InvalidConfigException('The "model" property must be set.');
        }
        if(!isset($this->options['upload']))
            $this->options['upload'] = true;
        if(!isset($this->options['ctype']))
            $this->options['ctype'] = false;
        if(!isset($this->options['visible']))
            $this->options['visible'] = true;
        if(!isset($this->options['answers']))
            $this->options['answers'] = true;

        $this->registerClientScript();
    }

    /**
     * @inheritdoc
     */
    public function run()
    {
        $class = \yii\helpers\StringHelper::basename(get_class($this->model));
        $data = Comments::getTree($this->model->id, $class);
        $models = $data[0];
        $countCtype = $data[1];

        $model = new Comments();
        $model->model_class = $class;
        $model->model_id = $this->model->id;

        return $this->render('index', [
            'model' => $model,
            'models' => $models,
            'countCtype' => $countCtype,
            'options' => $this->options
        ]);
    }

    /**
     * Register widget client scripts.
     */
    protected function registerClientScript()
    {
        Yii::$app->view->registerCssFile('/css/comments.css');
    }
}