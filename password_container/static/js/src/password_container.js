/* Javascript for PasswordContainerXBlock. */
"use strict"
var PasswordContainerXBlock = (function(){
    console.log('PasswordContainerXBlock initialization');

    var timeout;
    var TIME_LEFT_REFRESH = true;
    var TIME_LEFT_REFRESH_DELAY = 1 * 1000;

    /* generic ajax error method */
    var error = function(data) {
        console.log('error');
    }
    var checkPasswordUrl, getTimeLeftUrl, resetUserState;

    /* retrieve time left to complete quizz */
    var getTimeLeft = function(data) {

        window.clearTimeout(timeout);
        $.ajax({
            type: "POST",
            url: getTimeLeftUrl,
            data: JSON.stringify({'dummy': 'dummy'}),
            success: function(data) {
                $('#time-left').html(data.time_left);
            },
            error: error
        });
        timeout = window.setTimeout(getTimeLeft, TIME_LEFT_REFRESH_DELAY);
    }


    var CheckPassword = function(runtime, element) {
        console.log('xblock javascript initialization: CheckPassword');


        console.log(TIME_LEFT_REFRESH)

        if (TIME_LEFT_REFRESH) {
            timeout = window.setTimeout(getTimeLeft, 500);
        }

        $(element).find('.save-button').bind('click', function(event) {
            window.clearTimeout(timeout);
            var email = $(element).find('input[name=email]').val()
            var password = $(element).find('input[name=password]').val()
            var params = {
                email: email,
                password: password
            }
            console.log('checking password');
            $.ajax({
                type: "POST",
                url: checkPasswordUrl,
                data: JSON.stringify(params),
                success: function(data) {
                    console.log('success');
                    if (data.reload) {
                        document.location.reload(true);
                    } else {
                        console.log(data.i4x_uri)
                        var $element = $(document).find('[data-id="'+ data.i4x_uri +'"]');
                        $element.html(data.html);
                        if (TIME_LEFT_REFRESH) {
                            timeout = window.setTimeout(getTimeLeft, 500);
                        }
                    }
                },
                error: error
            });
        });
    };

    var Run = function(runtime, element) {

        console.log('xblock javascript initialization: Run');

        if (TIME_LEFT_REFRESH) {
            timeout = window.setTimeout(getTimeLeft, 500);
        }

        $(element).find('.reset-user-state').bind('click', function(event) {
            console.log('reseting user state');
            var params = {};
            $.ajax({
                type: "POST",
                url: resetUserState,
                data: JSON.stringify(params),
                success: function(data) {
                    console.log('user state reseted');
                    document.location.reload(true);
                },
                error: error
            });
        });

    };

    $(function ($) {
        /* Here's where you'd do things on page load. */
        console.log('document ready');

    });

    /* This is a hack/wrapper which allow us to have shared code between 2 functions called by XBlock initialization */
    /* functions to export */
    var x = {
        'Run': Run,
        'CheckPassword': CheckPassword,
    }
    var wrapper = function(runtime, element, method) {
        console.log('wrapper');
        console.log(method);

        checkPasswordUrl = runtime.handlerUrl(element, 'check_password');
        getTimeLeftUrl = runtime.handlerUrl(element, 'get_time_left');
        resetUserState = runtime.handlerUrl(element, 'reset_user_state');

        this[method](runtime, element);
    }.bind(x);
    return wrapper;
})();
