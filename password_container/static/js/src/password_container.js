/* Javascript for PasswordContainerXBlock. */
function CheckPassword(runtime, element) {

    var handlerUrl = runtime.handlerUrl(element, 'check_password');

    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
