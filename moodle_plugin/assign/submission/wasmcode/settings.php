<?php
defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {
    // Rust Evaluation Server URL
    $settings->add(new admin_setting_configtext(
        'assignsubmission_wasmcode/server_url',
        get_string('server_url', 'assignsubmission_wasmcode'),
        get_string('server_url_desc', 'assignsubmission_wasmcode'),
        'http://127.0.0.1:8080',
        PARAM_URL
    ));

    // Optional API Secret Key
    $settings->add(new admin_setting_configpasswordunmask(
        'assignsubmission_wasmcode/api_key',
        get_string('api_key', 'assignsubmission_wasmcode'),
        get_string('api_key_desc', 'assignsubmission_wasmcode'),
        ''
    ));

    // Default Execution Timeout (ms)
    $settings->add(new admin_setting_configtext(
        'assignsubmission_wasmcode/default_timeout_ms',
        get_string('default_timeout', 'assignsubmission_wasmcode'),
        get_string('default_timeout_desc', 'assignsubmission_wasmcode'),
        '2000',
        PARAM_INT
    ));

    // Default Memory Limit (MB)
    $settings->add(new admin_setting_configtext(
        'assignsubmission_wasmcode/default_memory_mb',
        get_string('default_memory', 'assignsubmission_wasmcode'),
        get_string('default_memory_desc', 'assignsubmission_wasmcode'),
        '64',
        PARAM_INT
    ));
}
