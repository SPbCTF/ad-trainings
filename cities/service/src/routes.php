<?php

use Slim\Http\Request;
use Slim\Http\Response;

// Routes

$app->get('/', function (Request $request, Response $response, array $args) {
    return $this->renderer->render($response, 'games.phtml');
});

$app->get('/{name:[0-9]+}', function (Request $request, Response $response, array $args) {
    // Sample log message
    $this->logger->info("City Game '/' route");

    if (!isset($this->map[$args['name']])) {
        return $this->renderer->render($response, 'error.phtml', $args)->withStatus(404);
    }
    // Render index view
    return $this->renderer->render($response, 'index.phtml', ['id' => $args['name'], 'country' => $this->map[$args['name']]]);
});

// Create new country
$app->get('/create/{countryname:[A-Za-z -.0-9]+}', function (Request $request, Response $response, array $args) {
    $max_key = max(array_keys($this->map)) + 1;
    exec("echo '".$args['countryname']."|".$max_key."' >> map.txt", $output);
    exec("touch countries/" . $max_key . ".txt", $output);
    return $response->withRedirect('/' . $max_key);
})->add(new \CountryCheck);

$app->get('/{name:[0-9]+}/{city}', function (Request $request, Response $response, array $args) {
    if (!isset($this->map[$args['name']])) {
        return $this->renderer->render($response, 'error.phtml', $args)->withStatus(404);
    }

    exec('cat countries/' . $args['name'] . '.txt | grep -i -E \'^'.$args['city'].'$\'', $output);
    if (!count($output)) {
//        Insert new city to cities list
        exec('echo \''.$args['city'].'\' >> countries/' . $args['name'] . '.txt', $output);
    }

    exec('cat countries/' . $args['name'] . '.txt | grep -i -E \'^'.substr($args['city'], -1).'.*$\'', $words);

    // Render index view
    return $this->renderer->render($response, 'index.phtml', [
            'country' => $this->map[$args['name']],
            'city' => $args['city'],
            'words' => $words,
            'id' => $args['name']
        ]
    );
});