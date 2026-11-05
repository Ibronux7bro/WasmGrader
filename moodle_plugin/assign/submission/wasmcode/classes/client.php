<?php
namespace assignsubmission_wasmcode;

defined('MOODLE_INTERNAL') || die();

class client {
    protected $server_url;
    protected $api_key;

    public function __construct() {
        $this->server_url = rtrim(get_config('assignsubmission_wasmcode', 'server_url'), '/');
        $this->api_key = get_config('assignsubmission_wasmcode', 'api_key');
        if (empty($this->server_url)) {
            $this->server_url = 'http://127.0.0.1:8080';
        }
    }

    /**
     * Submit code to Rust WASM evaluator server.
     *
     * @param string $language (c, cpp, rust, python)
     * @param string $source_code
     * @param array $test_cases
     * @param int $timeout_ms
     * @param int $memory_limit_mb
     * @return array Decoded response
     */
    public function evaluate($language, $source_code, array $test_cases, $timeout_ms = 2000, $memory_limit_mb = 64) {
        $payload = [
            'language' => strtolower($language),
            'source_code' => $source_code,
            'limits' => [
                'timeout_ms' => (int)$timeout_ms,
                'memory_limit_mb' => (int)$memory_limit_mb,
            ],
            'test_cases' => $test_cases,
        ];

        return $this->post('/api/v1/evaluate', $payload);
    }

    /**
     * Generate test cases via AI on the Rust backend.
     *
     * @param string $title
     * @param string $description
     * @param string $language
     * @param int $number_of_tests
     * @param string|null $reference_solution
     * @return array
     */
    public function generate_tests($title, $description, $language, $number_of_tests = 5, $reference_solution = null) {
        $payload = [
            'assignment_title' => $title,
            'assignment_description' => $description,
            'language' => strtolower($language),
            'number_of_tests' => (int)$number_of_tests,
            'reference_solution' => $reference_solution,
        ];

        return $this->post('/api/v1/tests/generate', $payload);
    }

    protected function post($endpoint, array $data) {
        $ch = curl_init($this->server_url . $endpoint);
        $headers = [
            'Content-Type: application/json',
            'Accept: application/json',
        ];

        if (!empty($this->api_key)) {
            $headers[] = 'Authorization: Bearer ' . $this->api_key;
        }

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            throw new \moodle_exception('server_connection_failed', 'assignsubmission_wasmcode', '', $error);
        }

        $decoded = json_decode($response, true);
        if ($http_code >= 400) {
            $msg = isset($decoded['error']) ? $decoded['error'] : 'HTTP Error ' . $http_code;
            throw new \moodle_exception('evaluator_error', 'assignsubmission_wasmcode', '', $msg);
        }

        return $decoded;
    }
}
