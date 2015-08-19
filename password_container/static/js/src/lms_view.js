function PasswordContainerLmsView(runtime, element) {
    var xblockSelector = 'div[data-usage-id="' + element.dataset.usageId +  '"] ';
    var resetUserStateUrl = runtime.handlerUrl(element, 'reset_user_state');
    var user_state_reset_button = $(xblockSelector + '.reset-user-state-button');
    user_state_reset_button.click(reset_user_state);
    
    function reset_user_state() {
	$.get(resetUserStateUrl,
	      {'username' : $(xblockSelector + '.username-input').val()},
	      function(data) {
		  $(xblockSelector + '.reset-user-state-response').html(data);
	      }, "html");
    }
}
