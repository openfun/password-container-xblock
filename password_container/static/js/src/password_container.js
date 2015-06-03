/* Javascript for PasswordContainerXBlock. */
"use strict"
var PasswordContainerXBlock = (function(){
    console.log('PasswordContainerXBlock initialization');

    /* common scope */
    var timeout;
    var TIME_LEFT_REFRESH = true;
    var TIME_LEFT_REFRESH_DELAY = 60 * 1000;
    var TIME_LEFT_WARNING_REFRESH_DELAY = 1 * 1000;
    var TIME_LEFT_WARNING = 60 * 5;

    /* generic ajax error handler */
    var errorHandler = function(data) {
        console.log('error');
    }
    var checkPasswordUrl, getTimeLeftUrl, resetUserState;

    var setTimeout = function(seconds_left) {
        var delay = seconds_left > TIME_LEFT_WARNING ? TIME_LEFT_REFRESH_DELAY : TIME_LEFT_WARNING_REFRESH_DELAY;
        timeout = window.setTimeout(getTimeLeft, delay);
    }

    /* retrieve time left to complete quizz */
    var getTimeLeft = function(data) {

        window.clearTimeout(timeout);
        $.ajax({
            type: "POST",
            url: getTimeLeftUrl,
            data: JSON.stringify({'dummy': 'dummy'}),
            success: function(data) {
                $('span#time-left').html(data.time_left);
                $('div#time-display').toggleClass('warning', data.warning);
                if (data.total <= 0) {
                    // time elapsed, reload the page to hide children
                    document.location.reload(true);
                } else {
                    setTimeout(data.total);
                }
            },
            error: errorHandler
        });
    }

    var bindResetButton = function(runtime, element) {
        console.log('DEBUG: binding reset button')
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
                error: errorHandler
            });
        });
    }


    /* will be called when user is asked to identify */
    var checkPassword = function(runtime, element) {
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
                    console.log('ajax success');
                    if (data.result) {
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
                    } else {
                        $(element).find('.password-nb-tries').text(data.nb_tries);
                        $(element).find('.password-error').text(data.message);
                        if (data.too_much_tries) {
                            document.location.reload(true);
                        }
                    }
                },
                error: errorHandler
            });
        });
    };


    /* will be called when user is identified and have limited time */
    var startExam = function(runtime, element) {

        console.log('xblock javascript initialization: Run');

        if (TIME_LEFT_REFRESH) {
            timeout = window.setTimeout(getTimeLeft, 500);
        }

        bindResetButton(runtime, element);
    };

    $(function ($) {
        console.log('document ready');

    });

    /* This wrapper allows us to have shared code and variables between 2 functions called by XBlock initialization */
    var methods = { /* functions to export */
        'startExam': startExam,
        'checkPassword': checkPassword,
        'bindResetButton': bindResetButton,
    }
    var wrapper = function(runtime, element, method) {
        // At xblock initialization we will receive runtime, DOM element and method to call
        console.log('wrapper:' + method);

        // store urls in common scope (WARNING urls are not really common. ie: multiple xblock instances on same page)
        checkPasswordUrl = runtime.handlerUrl(element, 'check_password');
        getTimeLeftUrl = runtime.handlerUrl(element, 'get_time_left');
        resetUserState = runtime.handlerUrl(element, 'reset_user_state');

        this[method](runtime, element);
    }.bind(methods);
    return wrapper;
})();
