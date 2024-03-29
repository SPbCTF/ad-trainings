<?php
// DIC configuration

$container = $app->getContainer();

// view renderer
$container['renderer'] = function ($c) {
    $settings = $c->get('settings')['renderer'];
    return new Slim\Views\PhpRenderer($settings['template_path']);
};

// monolog
$container['logger'] = function ($c) {
    $settings = $c->get('settings')['logger'];
    $logger = new Monolog\Logger($settings['name']);
    $logger->pushProcessor(new Monolog\Processor\UidProcessor());
    $logger->pushHandler(new Monolog\Handler\StreamHandler($settings['path'], $settings['level']));
    return $logger;
};

$container['map'] = function ($c) {
    exec("cat map.txt", $params);
    $dict = array_map(function ($el){ return explode('|', $el);}, $params);
    $map = array();
    foreach ($dict as $value) {
        $map[$value[1]] = $value[0];
    }
    return $map;
};