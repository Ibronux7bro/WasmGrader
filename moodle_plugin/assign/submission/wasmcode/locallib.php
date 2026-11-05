<?php
defined('MOODLE_INTERNAL') || die();

class assign_submission_wasmcode extends assign_submission_plugin {

    public function get_name() {
        return get_string('pluginname', 'assignsubmission_wasmcode');
    }

    public function get_settings(MoodleQuickForm $mform) {
        global $PAGE;

        // Assignment configuration settings for teacher
        $languages = [
            'c' => 'C (Clang / WASM)',
            'cpp' => 'C++ (Clang++ / WASM)',
            'rust' => 'Rust (wasm32-wasip1)',
            'python' => 'Python 3 (WASM)',
        ];

        $mform->addElement('select', 'assignsubmission_wasmcode_lang', get_string('language', 'assignsubmission_wasmcode'), $languages);
        $mform->setDefault('assignsubmission_wasmcode_lang', 'c');

        $mform->addElement('text', 'assignsubmission_wasmcode_timeout', get_string('timeout_ms', 'assignsubmission_wasmcode'));
        $mform->setType('assignsubmission_wasmcode_timeout', PARAM_INT);
        $mform->setDefault('assignsubmission_wasmcode_timeout', 2000);

        $mform->addElement('text', 'assignsubmission_wasmcode_memory', get_string('memory_limit_mb', 'assignsubmission_wasmcode'));
        $mform->setType('assignsubmission_wasmcode_memory', PARAM_INT);
        $mform->setDefault('assignsubmission_wasmcode_memory', 64);

        // Render AI Test Generator Modal Helper
        $modal_html = $PAGE->get_renderer('core')->render_from_template('assignsubmission_wasmcode/ai_generator_modal', []);
        $mform->addElement('static', 'assignsubmission_wasmcode_ai_btn', '', $modal_html);

        $mform->addElement('textarea', 'assignsubmission_wasmcode_tests', get_string('test_cases_json', 'assignsubmission_wasmcode'), ['rows' => 8, 'cols' => 60]);
        $mform->setType('assignsubmission_wasmcode_tests', PARAM_RAW);
        $mform->addHelpButton('assignsubmission_wasmcode_tests', 'test_cases_json', 'assignsubmission_wasmcode');

        $PAGE->requires->js_call_amd('assignsubmission_wasmcode/ai_generator', 'init', [
            ['cmid' => $this->assignment->get_course_module()->id]
        ]);
    }

    public function save_settings(stdClass $data) {
        $this->set_config('language', $data->assignsubmission_wasmcode_lang);
        $this->set_config('timeout_ms', $data->assignsubmission_wasmcode_timeout);
        $this->set_config('memory_limit_mb', $data->assignsubmission_wasmcode_memory);
        $this->set_config('test_cases', $data->assignsubmission_wasmcode_tests);
        return true;
    }

    public function get_form_elements_eval($submission, MoodleQuickForm $mform, stdClass $data, $formcontext) {
        global $DB, $PAGE;

        $current_code = '';
        if ($submission) {
            $record = $DB->get_record('assignsubmission_wasmcode', ['submission' => $submission->id]);
            if ($record) {
                $current_code = $record->source_code;
                $data->assignsubmission_wasmcode_code = $record->source_code;
            }
        }

        $language = $this->get_config('language') ?: 'c';
        $element_name = 'assignsubmission_wasmcode_code';
        $element_id = 'id_assignsubmission_wasmcode_code';

        $rendered_editor = $PAGE->get_renderer('core')->render_from_template('assignsubmission_wasmcode/submission_editor', [
            'element_name' => $element_name,
            'element_id' => $element_id,
            'language' => $language,
            'current_code' => $current_code,
        ]);

        $mform->addElement('static', 'assignsubmission_wasmcode_editor_view', '', $rendered_editor);

        $PAGE->requires->js_call_amd('assignsubmission_wasmcode/editor', 'init', [
            [
                'elementId' => $element_id,
                'cmid' => $this->assignment->get_course_module()->id,
            ]
        ]);

        return true;
    }

    public function save(stdClass $submission, stdClass $data) {
        global $DB;

        $source_code = $data->assignsubmission_wasmcode_code ?? '';

        // Save or update submission in database
        $record = $DB->get_record('assignsubmission_wasmcode', ['submission' => $submission->id]);
        if (!$record) {
            $record = new stdClass();
            $record->assignment = $this->assignment->get_instance()->id;
            $record->submission = $submission->id;
            $record->source_code = $source_code;
            $record->grade = 0;
            $record->timecreated = time();
            $record->timemodified = time();
            $record->id = $DB->insert_record('assignsubmission_wasmcode', $record);
        } else {
            $record->source_code = $source_code;
            $record->timemodified = time();
            $DB->update_record('assignsubmission_wasmcode', $record);
        }

        // Trigger Evaluation via Rust WASM Backend
        try {
            $client = new \assignsubmission_wasmcode\client();
            $language = $this->get_config('language') ?: 'c';
            $timeout = (int)($this->get_config('timeout_ms') ?: 2000);
            $memory = (int)($this->get_config('memory_limit_mb') ?: 64);
            $raw_tests = $this->get_config('test_cases') ?: '[]';
            $test_cases = json_decode($raw_tests, true) ?: [];

            $eval_result = $client->evaluate($language, $source_code, $test_cases, $timeout, $memory);

            // Update grade and log results
            $score = $eval_result['score_percentage'] ?? 0.0;
            $record->grade = $score;
            $record->evaluation_result = json_encode($eval_result);
            $DB->update_record('assignsubmission_wasmcode', $record);

            // Update Moodle Gradebook automatically
            $grade = $this->assignment->get_user_grade($submission->userid, true);
            $grade->grade = ($score / 100.0) * $this->assignment->get_instance()->grade;
            $this->assignment->update_grade($grade);

        } catch (\Exception $e) {
            \core\notification::error(get_string('eval_failed', 'assignsubmission_wasmcode') . ': ' . $e->getMessage());
        }

        return true;
    }

    public function view_summary(stdClass $submission, &$showviewlink) {
        global $DB;
        $record = $DB->get_record('assignsubmission_wasmcode', ['submission' => $submission->id]);
        if (!$record) {
            return get_string('no_submission', 'assignsubmission_wasmcode');
        }

        $html = html_writer::div(
            html_writer::tag('strong', get_string('score', 'assignsubmission_wasmcode') . ': ') .
            number_format($record->grade, 2) . '%',
            'wasmcode-score'
        );

        if (!empty($record->evaluation_result)) {
            $result = json_decode($record->evaluation_result, true);
            $summary = $result['summary'] ?? '';
            $html .= html_writer::div(s($summary), 'wasmcode-summary badge badge-info');
        }

        return $html;
    }
}
