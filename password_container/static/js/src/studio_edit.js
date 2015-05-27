/* Javascript for StudioEditableXBlockMixin. */
function PasswordContainerStudio(runtime, element) {
    "use strict";

    console.log('PasswordContainerStudio: init')
    $(element).find('#id_start_date_0').attr({'placeholder': 'MM/DD/YYY'}).addClass('hasDatepicker')
    $(element).find('#id_start_date_1').attr({'placeholder': 'HH:MM'}).addClass('ui-timepicker-input')
    $(element).find('#id_end_date_0').attr({'placeholder': 'MM/DD/YYY'}).addClass('hasDatepicker')
    $(element).find('#id_end_date_1').attr({'placeholder': 'HH:MM'}).addClass('ui-timepicker-input')
    // $( ".hasDatepicker" ).datepicker();
    var getExistingGroupUrl = runtime.handlerUrl(element, 'get_existing_group');
    $(element).find('#id_group_id').bind('keyup', function(e){
        var group_id = $(this).val();
        console.log(group_id)
        if (group_id !== '') {
            var data = {'group_id': group_id}
            $.ajax({
                type: "POST",
                url: getExistingGroupUrl,
                data: JSON.stringify(data),
                success: function(response) {
                    console.log(response);
                    if (response !== {}) {
                        $(element).find('#id_start_date_0').val(response.start_date_0);
                        $(element).find('#id_start_date_1').val(response.start_date_1);
                        $(element).find('#id_end_date_0').val(response.end_date_0);
                        $(element).find('#id_end_date_1').val(response.end_date_1);
                        $(element).find('#id_duration').val(response.duration);
                        $(element).find('#id_password').val(response.password);
                    }
                }
            });
        }
    });

    var studio_submit = function(data) {
        console.log('PasswordContainerStudio: submiting')

        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) {
                runtime.notify('save', {state: 'end'});
            }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    $('.save-button', element).bind('click', function(e) {
        console.log('PasswordContainerStudio: save')
        e.preventDefault();
        var fields = ['group_id', 'start_date_0', 'start_date_1', 'end_date_0', 'end_date_1', 'duration', 'password']
        var values = {};
        values['group_id'] = $(element).find('[name="group_id"]').val();
        values['start_date_0'] = $(element).find('[name="start_date_0"]').val();
        values['start_date_1'] = $(element).find('[name="start_date_1"]').val();
        values['end_date_0'] = $(element).find('[name="end_date_0"]').val();
        values['end_date_1'] = $(element).find('[name="end_date_1"]').val();
        values['duration'] = $(element).find('[name="duration"]').val();
        values['password'] = $(element).find('[name="password"]').val();
        studio_submit({values: values});
    });

    $(element).find('.cancel-button').bind('click', function(e) {
        console.log('PasswordContainerStudio: cancel')

        e.preventDefault();
        runtime.notify('cancel', {});
    });
}
