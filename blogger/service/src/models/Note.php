<?php

namespace app\models;

use Yii;
use yii\base\Model;

/**
 * This is the model class for table "note".
 *
 * @property integer $id
 * @property string $note
 */
class Note extends Model
{

    public function rules()
    {
        return [
            [['note'], 'string', 'max'=>256]
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'note' => 'Note'
        ];
    }
}
