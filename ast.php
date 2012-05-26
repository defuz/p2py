<?php


require dirname(__FILE__) . '/PHPParser/Autoloader.php';
PHPParser_Autoloader::register();

$code = file_get_contents($argv[1]);

$parser = new PHPParser_Parser(new PHPParser_Lexer);
$serializer = new PHPParser_Serializer_JSON;

try {
    $tree = $parser->parse($code);
    echo $serializer->serialize($tree);
} catch (PHPParser_Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}


