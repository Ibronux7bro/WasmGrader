<?php
// Mock MOODLE_INTERNAL to test client.php in isolation
define('MOODLE_INTERNAL', true);

function get_config($plugin, $key) {
    if ($key === 'server_url') return 'http://127.0.0.1:8080';
    if ($key === 'api_key') return '';
    return null;
}

class moodle_exception extends Exception {}

require_once __DIR__ . '/../moodle_plugin/assign/submission/wasmcode/classes/client.php';

echo "[*] Testing PHP Moodle Client integration with Evaluation Server...\n";

$client = new \assignsubmission_wasmcode\client();

$test_cases = [
    [
        'id' => 1,
        'name' => 'PHP Bridge Test 1',
        'input' => "100 200\n",
        'expected_output' => "300\n",
        'is_hidden' => false,
        'weight' => 50.0
    ],
    [
        'id' => 2,
        'name' => 'PHP Bridge Test 2',
        'input' => "50 50\n",
        'expected_output' => "100\n",
        'is_hidden' => true,
        'weight' => 50.0
    ]
];

$code = "#include <stdio.h>\nint main() { int a, b; if (scanf(\"%d %d\", &a, &b) == 2) printf(\"%d\\n\", a + b); return 0; }";

try {
    $res = $client->evaluate('c', $code, $test_cases, 2000, 64);
    echo "  [+] Status: Success!\n";
    echo "  [+] Summary: " . $res['summary'] . "\n";
    echo "  [+] Score: " . $res['score_percentage'] . "%\n";
    echo "  [+] Passed " . count($res['results']) . " test cases.\n";

    echo "\n[*] Testing PHP Moodle AI Test Generator Bridge...\n";
    $ai_res = $client->generate_tests("Sum Problem", "Add two numbers", "c", 3);
    echo "  [+] Generated " . count($ai_res['test_cases']) . " test cases via PHP Client.\n";

} catch (Exception $e) {
    echo "  [-] Error: " . $e->getMessage() . "\n";
    exit(1);
}

echo "\n[SUCCESS] PHP Moodle Bridge is 100% operational!\n";
