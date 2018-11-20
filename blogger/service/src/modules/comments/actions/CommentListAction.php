<?php

namespace app\modules\comments\actions;

use app\modules\api\actions\ApiAction;
use app\modules\comments\models\Comments;
use Yii;


class CommentListAction extends ApiAction
{

    public function init()
    {
        $this->ajaxOnly = true;
        $this->jsonOnly = true;
        return parent::init();
    }

    public function run($model, $id)
    {
        $data = Comments::getTree($id, $model);

        $result = $this->convert($data[0]);


        return $this->render([$result, $data[1]]);
    }


    private function convert($data)
    {
        $result = [];
        foreach($data as $d){
            $temp = $d->getAttributes();

            if($d->children)
                $temp['children'] = $this->convert($d->children);
            $result[] = $temp;
        }
        return $result;
    }

}