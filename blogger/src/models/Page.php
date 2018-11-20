<?php

namespace app\models;

use Yii;
use yii\base\Model;

/**
 * This is the model class for table "page".
 *
 * @property integer $id
 * @property string $title
 * @property string $description
 */
class Page extends Model
{
    public $id = 1;
    public $title = "Blog";
    public $description = "Text of blog";

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'title' => 'Title',
            'description' => 'Description',
        ];
    }
}
