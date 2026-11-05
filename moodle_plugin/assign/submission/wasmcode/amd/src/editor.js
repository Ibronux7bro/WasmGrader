/**
 * Moodle AMD module for WASM Code Submission Editor and AJAX runner.
 */
define(['jquery', 'core/ajax', 'core/notification'], function($, ajax, notification) {
    'use strict';

    return {
        init: function(config) {
            var $editor = $('#' + config.elementId);
            var $btnTest = $('#btn-test-run');
            var $console = $('#wasm-test-console');
            var $consoleOutput = $('#wasm-console-output');
            var $statusBadge = $('#wasm-run-status');

            $btnTest.on('click', function(e) {
                e.preventDefault();
                var code = $editor.val();
                if (!code.trim()) {
                    alert('Please write code before running tests.');
                    return;
                }

                $btnTest.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Running in Sandbox...');
                $console.removeClass('d-none');
                $consoleOutput.text('Compiling to WASM and executing in sandbox...');
                $statusBadge.removeClass('bg-success bg-danger').addClass('bg-warning').text('Running');

                // Call Moodle AJAX service or direct API
                $.ajax({
                    url: M.cfg.wwwroot + '/mod/assign/submission/wasmcode/ajax.php?action=run_public',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        sesskey: M.cfg.sesskey,
                        cmid: config.cmid,
                        code: code
                    },
                    success: function(resp) {
                        $btnTest.prop('disabled', false).html('<i class="fa fa-play me-1"></i> Run Tests');
                        if (resp.success) {
                            $statusBadge.removeClass('bg-warning bg-danger').addClass('bg-success').text('Passed: ' + resp.score_percentage + '%');
                            $consoleOutput.text(resp.summary + "\n\n" + JSON.stringify(resp.results, null, 2));
                        } else {
                            $statusBadge.removeClass('bg-warning bg-success').addClass('bg-danger').text('Failed');
                            var errorMsg = resp.compilation ? resp.compilation.compiler_output : resp.summary;
                            $consoleOutput.text(errorMsg);
                        }
                    },
                    error: function(xhr, status, error) {
                        $btnTest.prop('disabled', false).html('<i class="fa fa-play me-1"></i> Run Tests');
                        $statusBadge.removeClass('bg-warning bg-success').addClass('bg-danger').text('Error');
                        $consoleOutput.text('Server Error: ' + error);
                    }
                });
            });
        }
    };
});
