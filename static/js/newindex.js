var main = function () {

	$.ajax({
		    url: "/api/game_status",
		    dataType: "json",
	        success: function(data){
	        	$('#timerDiv').timer({
					format: '%H:%M:%S',
					duration: data.remaining,
					countdown: true
				})

		    }
	});

	$.ajax({
		    url: "/api/gap",
		    dataType: "json",
	        success: function(data){
	        	$('#gap').text(data.gap)
		    }
	});
	$.ajax({
		    url: "/api/delta",
		    dataType: "json",
	        success: function(data){
	        	$('#delta').text(data.delta)
		    }
	});
	$.ajax({
		    url: "/api/hunt_status",
		    dataType: "json",
	        success: function(data) {
	        	if (data.hunt_active) {
	        		$('.hunt-bar').show();
	        	}
		    }
	});



}


$(document).ready(main);