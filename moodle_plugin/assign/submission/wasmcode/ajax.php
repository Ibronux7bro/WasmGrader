<?php
define('AJAX_SCRIPT', true);
require_once(__DIR__ . '/../../../../config.php');
require_once($CFG->dirroot . '/mod/assign/locallib.php');
require_once(__DIR__ . '/locallib.php');

require_sesskey();

$action = required_param('action', PARAM_ALPHAEXT);
$cmid = required_param('cmid', PARAM_INT);

list($course, $cm) = get_course_and_cm_from_cmid($cmid, 'assign');
require_login($course, false, $cm);
$context = context_module::instance($cm->id);

$client = new \assignsubmission_wasmcode\client();
$assign = new assign($context, $cm, $course);
$plugin = $assign->get_submission_plugin_by_type('wasmcode');

header('Content-Type: application/json; charset=utf-8');

try {
    if ($action === 'run_public') {
        $code = required_param('code', PARAM_RAW);
        $language = $plugin->get_config('language') ?: 'c';
        $timeout = (int)($plugin->get_config('timeout_ms') ?: 2000);
        $memory = (int)($plugin->get_config('memory_limit_mb') ?: 64);
        $raw_tests = $plugin->get_config('test_cases') ?: '[]';
        $all_tests = json_decode($raw_tests, true) ?: [];

        // Filter only public test cases for the student preview run
        $public_tests = array_filter($all_tests, function($tc) {
            return empty($tc['is_hidden']);
        });

        $result = $client->evaluate($language, $code, array_values($public_tests), $timeout, $memory);
        echo json_encode($result);
        exit;

    } else if ($action === 'generate_tests') {
        require_capability('mod/assign:grade', $context);

        $num_tests = optional_param('number_of_tests', 5, PARAM_INT);
        $ref_sol = optional_param('reference_solution', '', PARAM_RAW);
        $language = $plugin->get_config('language') ?: 'c';
        $title = $assign->get_instance()->name;
        $description = $assign->get_instance()->intro;

        $result = $client->generate_tests($title, $description, $language, $num_tests, $ref_sol);
        echo json_encode($result);
        exit;

    } else {
        http_response_code(400);
        echo json_encode(['error' => 'Unknown action']);
        exit;
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
    exit;
}
