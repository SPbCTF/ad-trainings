<?php
$rootPath = __DIR__.'/..';

require($rootPath.'/vendor/autoload.php');
require($rootPath.'/config/env.php');

defined('YII_DEBUG') or define('YII_DEBUG', true);
defined('YII_ENV') or define('YII_ENV', getenv('YII_ENV'));

require($rootPath.'/vendor/yiisoft/yii2/Yii.php');

$config = require($rootPath.'/config/main.php');
$application = new yii\web\Application($config);
$application->run();
