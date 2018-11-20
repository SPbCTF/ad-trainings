<?php

namespace app\models;

use Yii;
use yii\base\Model;


class NoteForm extends Model
{
    public $txt;
    public $ident;

    /**
     * @return array the validation rules.
     */
    public function rules()
    {
        return [
            [['txt', 'ident'], 'required'],
            [['txt'], 'string', 'max'=>256],
            [['ident'], 'string', 'max'=>32],
        ];
    }

    public function attributeLabels()
    {
        return [
            'txt' => 'Текст заметки',
        ];
    }

}
