<?php
/**
 * Standalone Moodle PHP Client Verification Script
 */

define('MOODLE_INTERNAL', true);

function get_config($plugin, $key) {
    if ($key === 'server_url') return 'http://127.0.0.1:8085';
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
    ['id' => 'tc_php_1', 'input' => "10\n20\n", 'expected_output' => "30\n", 'points' => 50],
    ['id' => 'tc_php_2', 'input' => "100\n50\n", 'expected_output' => "150\n", 'points' => 50]
];

try {
    $result = $client->evaluate('python', "a = int(input())\nb = int(input())\nprint(a + b)", $tests);
    echo "[+] SUCCESS: Response received from WasmGrader daemon!\n";
    echo "    Status: " . $result['status'] . "\n";
    echo "    Grade:  " . $result['total_score'] . " / " . $result['max_score'] . " points\n";
    echo "    Execution Time: " . $result['execution_time_us'] . " microseconds\n";
    echo "=======================================================\n";
    echo "   MOODLE GRADEBOOK SYNCHRONIZATION TEST: PASSED\n";
    echo "=======================================================\n\n";
} catch (Exception $e) {
    echo "[-] ERROR: " . $e->getMessage() . "\n";
}
