<?php

use yii\db\Schema;
use yii\db\Migration;

class m150825_070358_create_comments extends Migration
{
    public function up()
    {
        $this->createTable('data_comments',[
            'id' => Schema::TYPE_PK,
            'model_class' => 'varchar(32) NOT NULL',
            'model_id' => Schema::TYPE_INTEGER . ' NOT NULL',
            'created' => Schema::TYPE_TIMESTAMP . ' NULL DEFAULT CURRENT_TIMESTAMP',
            'txt' => Schema::TYPE_TEXT . ' NOT NULL',
            'user_id' => Schema::TYPE_INTEGER . ' NOT NULL',
        ]);
    }

    public function down()
    {
        $this->dropTable('data_comments');

        return false;
    }

}
