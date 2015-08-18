function responseHandler(responseText, statusText, xhr, $form) {
	if (responseText["status"] == "success") {
		$('#statusLine').text("OK")	
	} else {
		$('#statusLine').text(responseText["msg"])	
	}	
}


var main = function () {
	$('#newPlayer').click(function() {
		var lastId = $('#fieldsets').children('fieldset').last().children('.radio')[0].value;

		var newElem = $('<fieldset>').append($('<input>', {'type':'text', 'name':'players'}))
			.append($('<input>', {'type':'radio','class':'radio','name':'mrx_pos','value':parseInt(lastId)+1}));
		$(newElem).appendTo($('#fieldsets'));
	});

	$('#myForm').ajaxForm({success: responseHandler, dataType:'json'});
};


$(document).ready(main);