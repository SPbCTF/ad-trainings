<?php

namespace app\modules\comments\models;

use app\models\SuperPuperUserPyser;

use Yii;

/**
 * This is the model class for table "data_comments".
 *
 * @property integer $id
 * @property integer $pid
 * @property string $model_class
 * @property integer $model_id
 * @property string $created
 * @property integer $ctype
 * @property integer $state
 * @property string $title
 * @property string $txt
 * @property string $attachment
 * @property integer $likes
 * @property integer $user_id
 */
class Comments extends \yii\db\ActiveRecord
{
    const CTYPE_POSITIVE = 0;
    const CTYPE_NEGATIVE = 1;
    const CTYPE_NEUTRAL = 2;

    /**
     * @inheritdoc
     */
    public $children;

    public static function tableName()
    {
        return 'data_comments';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['model_class', 'model_id', 'txt', 'user_id'], 'required', 'message'=>'Заполните поле'],
            [['txt'], 'string'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'model_class' => 'Model Class',
            'model_id' => 'Model ID',
            'created' => 'Created',
            'txt' => 'Txt',
            'user_id' => 'User ID',
        ];
    }

    public static function getCtypes()
    {
        return [
            self::CTYPE_POSITIVE => 'Good',
            self::CTYPE_NEGATIVE => 'Negative',
            self::CTYPE_NEUTRAL  => 'Neutral',
        ];
    }

    public function getAuthor()
    {
        return $this->user_id ? SuperPuperUserPyser::findIdentity($this->user_id) : false;
    }

    public function getDate()
    {
//        setlocale(LC_ALL, 'rus');
//        setlocale(LC_ALL, 'ru_RU.UTF8');
        $x = $this->created;
//        $x = strtotime($x);
//        $x = strftime('%e %B %Y | %H:%M', $x);
        return $x;
    }

    public function getLogin()
    {
        $u = $this->author;
        return $u ? $u->username : 'Anonymous';
    }

    public function getAttach()
    {

        return array();

    }

    public function getAuthorPhoto()
    {
        $u = $this->author;
        return $u ? '/anon.jpg' : '';
    }

    public static function getTree($id, $class, $counter = false)
    {
        $models = self::find()->where([
            'model_id' => $id,
            'model_class' => $class
        ])->orderBy(['created' => SORT_DESC])->limit(20)->all();
        $countCtype = NULL;
        if($counter)
            $countCtype = self::getCountCtype($models);
        if (false && $models !== null) {
            $models = self::buildTree($models);
        }
        return [$models, $countCtype];
    }

    protected static function buildTree(&$data, $rootID = 0)
    {
        $tree = [];
        foreach ($data as $id => $node) {
            if ($node->pid == $rootID) {
                unset($data[$id]);
                $node->children = self::buildTree($data, $node->id);
                $tree[] = $node;
            }
        }
        return $tree;
    }

    public static function getCountCtype($models = array())
    {
        $data = [0, 0, 0];
        foreach($models as $model)
            $data[$model->ctype] += 1;
        return $data;
    }
}
