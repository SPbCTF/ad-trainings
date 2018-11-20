<?php

use yii\db\Schema;
use yii\db\Migration;

class m150825_070359_notes extends Migration
{
    public function up()
    {
        $this->createTable('notes',[
            'id' => Schema::TYPE_PK,
            'note' => 'varchar(32) NOT NULL',
            'user_id' => Schema::TYPE_INTEGER . ' NOT NULL',
        ]);
    }

    public function down()
    {
        $this->dropTable('notes');

        return false;
    }

}
