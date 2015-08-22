var map;

function takeTaskHandler(data) {
	if (data.status == "success") {
		alert("OK");
		location.reload();
	} else {
		alert(data.msg);
	}
}

function answerHandler(data) {
	if (data.status == "success") {
		alert("OK");
		location.reload();
	} else {
		alert(data.msg);
	}	
}

function codeHandler(data) {
	if (data.status == "success") {
		alert("OK");
		location.reload();
	} else {
		alert(data.msg);
	}	
}

function taskCircleCallback(taskId) {
	return function(e) {
				for (var i = 0; i < map.polygons.length; i++) {
					polygon = map.polygons[i];
					polygon.setOptions({
						strokeWeight:1,
						strokeOpacity: 0.5,
						strokeColor: polygon.fillColor});	
				}

				this.setOptions({
					strokeWeight:3,
					strokeOpacity: 1,
					strokeColor: "#FF0000"
					});

			    $('.task-button').show()
			    $('#takeTaskButton').text("Investigate " + taskId)
			    $('#takeTaskButton').off('click').click(function() {
			    	$.ajax({
					 	type: "POST",
					 	url: "/api/task/take",
					 	data: {id:taskId},
					 	success: takeTaskHandler,
					 	dataType: "json"
					});
			    })

			  }	
}

function handleTasks(data) {

	var activeTask = undefined;
	var requestedTask = undefined;

	for (i = 0; i < data.length; i++) {
		var taskId = data[i].id;

		var color;

		switch (data[i].task_status) {
			case "pending": color = "#F59000"; break;
			case "requested": color = "#CC0000"; break;
			case "active": color = "#CC0000"; break;
			case "cancelled": color = "#666666"; break;
			case "completed": color = "#33CC33"; break;
		}

		var circle = map.drawCircle({
			id: data[i].id,
			lat: data[i].lat,
			lng: data[i].lng,
			radius: data[i].radius,
			strokeColor: color,
            strokeOpacity: 0.5,
            strokeWeight: 1,
            fillColor: color,
            fillOpacity: 0.2,
            click: taskCircleCallback(data[i].id)
			});

		if (data[i].task_status == "active") {
			activeTask = data[i];
		}
		if (data[i].task_status == "requested") {
			requestedTask = data[i];
		}
	}

	

	if (activeTask != undefined) {
		$('.task-timer').hide();
		$('.task-img').attr("src",activeTask.img_url);
		$('#task-img-link').attr("href",activeTask.img_url);
		$('#answerInput').removeAttr('disabled');
		$('#cancelButton').removeAttr('disabled');
		$('#cancelButton').off('click').click(function() {
			$.ajax({
				type: "POST",
				url: "/api/task/cancel",
				data: {id:activeTask.id},
					success: function(data) {
						location.reload();
					},
			 	dataType: "json"
				});	
		});
		$('#answerButton').removeAttr('disabled');
		$('#answerButton').off('click').click(function() {
			var answer = $('#answerInput').val();
			$.ajax({
				type: "POST",
				url: "/api/task/answer",
				data: {id:activeTask.id, answer:answer},
				success: answerHandler,
			 	dataType: "json"
				});	
		});
	}

	if (requestedTask != undefined) {
		$('.task-timer').show();
		$('#cancelButton').removeAttr('disabled');
		$('#cancelButton').off('click').click(function() {
			$.ajax({
				type: "POST",
				url: "/api/task/cancel",
				data: {id:requestedTask.id},
					success: function(data) {
						location.reload();
					},
			 	dataType: "json"
				});	
		});
		$('#taskTimerDiv').countdown({
			until: requestedTask.remaining,
			compact:true,
			onExpiry: function() {location.reload()}});

	}

}

function getErrorMessage(error) {

	var errorMessage = "";
	switch(error.code) {
		case error.PERMISSION_DENIED:
			errorMessage = "User denied the request for Geolocation.";
			break;
		case error.POSITION_UNAVAILABLE:
			errorMessage = "Location information is unavailable.";
			break;
		case error.TIMEOUT:
			errorMessage = "The request to get user location timed out.";
			break;
		case error.UNKNOWN_ERROR:
			errorMessage = "An unknown error occurred.";
			break;
	}

	return errorMessage;
}

function locError(error) {
	var errorMessage = getErrorMessage(error);
	// tell the user if the current position could not be located
	alert("Error occurred: " + errorMessage + "\nThe current position could not be found.\nPlease turn GPS on.");
}

function displayPosition(lat, lng, isPanTo, isMrx) {
	var imgUrl;
	if (isMrx) {
		imgUrl = 'static/image/pegman.png';
	} else {
		imgUrl = 'static/image/pegman_sherlock.png';
	}

	console.log()

	var image = {
		url: imgUrl,
		size: new google.maps.Size(40, 50),
		origin: new google.maps.Point(0,0),
		anchor: new google.maps.Point(20, 50)
	};
	var shape = {
		coords: [1, 1, 1, 50, 40, 50, 40 , 1],
		type: 'poly'
	};


	var marker = map.addMarker({
		lat: lat,
		lng: lng,
		icon: image
	});
		
	if (isPanTo) {
		map.panTo(new google.maps.LatLng(
				lat,
				lng
			));
	}	
}

function sendAndDisplay(isFirstTime) {
	return function(position) {
		$.ajax({
			type: "POST",
			url: "/api/send_location",
			data: {
				lat: position.coords.latitude,
				lng: position.coords.longitude
			}
			});

		// set current position
		displayPosition(position.coords.latitude, position.coords.longitude, isFirstTime, false);
	}

	// watch position
	// watchCurrentPosition();
}

function handleGeoposition(isFirstTime) {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			sendAndDisplay(isFirstTime),
			locError,
			{
				timeout: 10000,
				enableHighAccuracy: true,
				maximumAge: Infinity
			});
	} else {
		// tell the user if a browser doesn't support this amazing API
		locError();
	}
}

function updateStatusBar() {
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

	        		console.log(data);
	        		if (data.hasOwnProperty("lat")) {
	        			displayPosition(data.lat, data.lng, false, true)
	        		}
	        	}
		    }
	});

}

var main = function () {

	$.ajax({
		    url: "/api/game_status",
		    dataType: "json",
	        success: function(data){
	        	$('#timerDiv').countdown({
	        		until: data.remaining, 
	        		compact:true,
	        		onExpiry: function() {location.reload()}
	        	});

		    }
	});

	$.ajax({
		    url: "/api/task/list",
		    dataType: "json",
	        success: handleTasks
	});

	$('#codeSubmitButton').click(function() {
			$.ajax({
				type: "POST",
				url: "/api/submit_mrx_code",
				data: {code:$('#codeInput').val()},
				success: codeHandler,
			 	dataType: "json"
				});	
		});

	map = new GMaps({
		  	div: '#map-canvas',
		  	lat: 55.754365,
		  	lng: 37.620041
			});

	handleGeoposition(true);
	setInterval(function() {handleGeoposition(false)}, 30000);

	updateStatusBar();
	setInterval(updateStatusBar, 30000);
}


$(document).ready(main);