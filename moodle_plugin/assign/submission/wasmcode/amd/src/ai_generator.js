/**
 * Moodle AMD module for Teacher AI Test Case Generator dialog.
 */
define(['jquery', 'core/notification'], function($, notification) {
    'use strict';

    return {
        init: function(config) {
            var $openBtn = $('#btn-open-ai-modal');
            var $generateBtn = $('#btn-ai-submit-generate');
            var $applyBtn = $('#btn-ai-apply-tests');
            var $previewContainer = $('#ai-preview-container');
            var $previewList = $('#ai-preview-list');
            var $spinner = $('#ai-spinner');
            var $modalEl = $('#wasmAiModal');
            var generatedData = null;

            $openBtn.on('click', function(e) {
                e.preventDefault();
                var modal = new bootstrap.Modal($modalEl[0]);
                modal.show();
            });

            $generateBtn.on('click', function() {
                var testCount = $('#ai-test-count').val() || 5;
                var refSol = $('#ai-reference-sol').val() || '';

                $generateBtn.prop('disabled', true);
                $spinner.removeClass('d-none');

                $.ajax({
                    url: M.cfg.wwwroot + '/mod/assign/submission/wasmcode/ajax.php?action=generate_tests',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        sesskey: M.cfg.sesskey,
                        cmid: config.cmid,
                        number_of_tests: testCount,
                        reference_solution: refSol
                    },
                    success: function(resp) {
                        $generateBtn.prop('disabled', false);
                        $spinner.addClass('d-none');

                        if (resp && resp.test_cases) {
                            generatedData = resp.test_cases;
                            $previewList.empty();
                            resp.test_cases.forEach(function(tc) {
                                var badge = tc.is_hidden 
                                    ? '<span class="badge bg-secondary">Hidden</span>' 
                                    : '<span class="badge bg-info">Public</span>';

                                var item = '<div class="list-group-item list-group-item-action">' +
                                    '<div class="d-flex w-100 justify-content-between">' +
                                    '<h6 class="mb-1">' + tc.name + '</h6>' + badge + '</div>' +
                                    '<small class="font-monospace text-muted">Input: ' + tc.input.replace(/\n/g, '\\n') + '</small><br>' +
                                    '<small class="font-monospace text-success">Output: ' + tc.expected_output.replace(/\n/g, '\\n') + '</small>' +
                                    '</div>';
                                $previewList.append(item);
                            });

                            $previewContainer.removeClass('d-none');
                            $applyBtn.removeClass('d-none');
                        } else {
                            alert('Failed to generate test cases.');
                        }
                    },
                    error: function(xhr, status, error) {
                        $generateBtn.prop('disabled', false);
                        $spinner.addClass('d-none');
                        alert('Error contacting AI service: ' + error);
                    }
                });
            });

            $applyBtn.on('click', function() {
                if (generatedData) {
                    var jsonString = JSON.stringify(generatedData, null, 2);
                    $('#id_assignsubmission_wasmcode_tests').val(jsonString);
                    var modal = bootstrap.Modal.getInstance($modalEl[0]);
                    if (modal) {
                        modal.hide();
                    }
                }
            });
        }
    };
});
