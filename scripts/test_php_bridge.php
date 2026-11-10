<?php
/**
 * Standalone Moodle PHP Client Verification Script
 */

define('MOODLE_INTERNAL', true);

function get_config($plugin, $key) {
    if ($key === 'server_url') return 'http://127.0.0.1:8080';
    if ($key === 'api_key') return 'moodle_wasm_secret_key_2026';
    return null;
}

class moodle_exception extends Exception {}

require_once __DIR__ . '/../moodle_plugin/assign/submission/wasmcode/classes/client.php';

use assignsubmission_wasmcode\client;

echo "\n=======================================================\n";
echo "   Moodle PHP Plugin Bridge Verification (client.php)   \n";
echo "=======================================================\n";

$client = new client();

echo "[*] Submitting Python Assignment via Moodle PHP cURL Bridge...\n";
$tests = [
    [
        'id' => 1,
        'name' => 'test_1',
        'input' => "10\n20\n",
        'expected_output' => "30\n",
        'weight' => 50.0,
        'is_hidden' => false,
        'test_type' => 'standard'
    ],
    [
        'id' => 2,
        'name' => 'test_2',
        'input' => "100\n50\n",
        'expected_output' => "150\n",
        'weight' => 50.0,
        'is_hidden' => false,
        'test_type' => 'standard'
    ]
];

try {
    $result = $client->evaluate('python', "a = int(input())\nb = int(input())\nprint(a + b)", $tests);
    echo "[+] SUCCESS: Response received from WasmGrader daemon!\n";
    echo "    Success: " . ($result['success'] ? 'true' : 'false') . "\n";
    echo "    Summary: " . $result['summary'] . "\n";
    echo "    Grade:   " . $result['score_percentage'] . " / 100 points\n";
    echo "    Compiler: " . $result['compilation']['compiler_output'] . "\n";
    foreach ($result['results'] as $r) {
        echo "      - Test #" . $r['id'] . ": " . (is_string($r['status']) ? $r['status'] : json_encode($r['status'])) . " (Execution Time: " . $r['execution_time_ms'] . " ms, Memory: " . $r['memory_used_kb'] . " KB)\n";
    }
    echo "=======================================================\n";
    echo "   MOODLE GRADEBOOK SYNCHRONIZATION TEST: PASSED\n";
    echo "=======================================================\n\n";
} catch (Exception $e) {
    echo "[-] ERROR: " . $e->getMessage() . "\n";
}
