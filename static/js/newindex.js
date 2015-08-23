var map,
	currentPositionMarker,
	mrxMarker;

Number.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    = hours+':'+minutes+':'+seconds;
    return time;
}

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
			if (confirm("Are you sure? You won't be able to get back to this task in the furute")) {
				$.ajax({
					type: "POST",
					url: "/api/task/cancel",
					data: {id:activeTask.id},
						success: function(data) {
							location.reload();
						},
				 	dataType: "json"
					});	
			}
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

function createNewMarker(lat, lng, isPanTo, isMrx) {
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
		icon: image,
	});
		
	if (isPanTo) {
		map.panTo(new google.maps.LatLng(
				lat,
				lng
			));
	}

	return marker;	
}

function handleSendGeoposition() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			function(position) {
				$.ajax({
					type: "POST",
					url: "/api/send_location",
					data: {
						lat: position.coords.latitude,
						lng: position.coords.longitude
					}
					});
			},
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
	        			if (mrxMarker == undefined) {
	        				mrxMarker = createNewMarker(data.lat, data.lng, false, true)
	        			} else {
	        				mrxMarker.setPosition(
								new google.maps.LatLng(
									data.lat,
									data.lng)
							);
	        			}
	        		}
	        	}
		    }
	});

}

function errorCallback(error) {
	var errorMessage = getErrorMessage(error);

	if (error.TIMEOUT) {
		// Acquire a new position object.
		navigator.geolocation.getCurrentPosition(
			watchCurrentPosition,
			errorCallback,
			{
				timeout: 1000,
				enableHighAccuracy: true,
				maximumAge: Infinity
			});
	}

	// tell the user if the current position could not be located
	console.log("Error occured: " + errorMessage);
}

function watchCurrentPosition() {
	var positionTimer = navigator.geolocation.watchPosition(
		function (position) {
			if (currentPositionMarker == undefined) {
				currentPositionMarker = createNewMarker(position.coords.latitude, position.coords.longitude, true, false);
			} else {
				currentPositionMarker.setPosition(
					new google.maps.LatLng(
						position.coords.latitude,
						position.coords.longitude)
				);
			}
		},
		errorCallback,
		{
			timeout: 1000,
			enableHighAccuracy: true,
			maximumAge: Infinity
		});
}

var main = function () {

	$.ajax({
		    url: "/api/game_status",
		    dataType: "json",
	        success: function(data){
	        	if (data.game_status == "active") {
		        	$('#timerDiv').countdown({
		        		until: data.remaining, 
		        		compact:true,
		        		onExpiry: function() {location.reload()}
		        	});
	        	} else {
	        		$('#timerDiv').text(data.remaining.toHHMMSS())
	        	}

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

	handleSendGeoposition(true);
	setInterval(function() {handleSendGeoposition(false)}, 30000);

	updateStatusBar();
	setInterval(updateStatusBar, 30000);

	watchCurrentPosition();
}


$(document).ready(main);