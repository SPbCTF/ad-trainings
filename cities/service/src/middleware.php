<?php
// Application middleware

Class CountryCheck
{
    public function __invoke($request, $response, $next)
    {
        $route = $request->getAttribute('route');
        $arguments = $route->getArguments();
        exec('cat map.txt | grep -i -E \'^'.$arguments['countryname'].'\|\'', $countries);

        if (count($countries)===0)
            $response = $next($request, $response);
        else {
            $response->getBody()->write('Country '.$arguments['countryname'].' exists');
            return $response->withStatus(403);
        }

        return $response;
    }
}