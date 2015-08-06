// you can specify the default latitude and longitude
var map,
	currentPositionMarker,
	currentPositionMarkerInfoWindow
	mapCenter = new google.maps.LatLng(55.754365, 37.620041),
	map;

// change the zoom if you want
function initializeMap()
{
	map = new google.maps.Map(document.getElementById('map-canvas'), {
		zoom: 15,
		center: mapCenter,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		disableDefaultUI: true,
		zoomControl: true,
		zoomControlOptions: {
			style: google.maps.ZoomControlStyle.SMALL,
			position: google.maps.ControlPosition.RIGHT_CENTER
		}
	});

	setTaskMarkers(map);
}

function setTaskMarkers(map) {
	sendGetRequest(function(responseText){
		var tasks = JSON.parse(responseText);
		console.log(tasks);
		drawTaskMarkers(map, tasks);
	}, '/task', true);
}

function drawTaskMarkers(map, tasks) {
    // Add tasks to the map

    // Marker sizes are expressed as a Size of X,Y
    // where the origin of the image (0,0) is located
    // in the top left of the image.

    // Origins, anchor positions and coordinates of the marker
    // increase in the X direction to the right and in
    // the Y direction down.
    var image = {
        url: 'static/image/beachflag.png',
        // This marker is 20 pixels wide by 32 pixels tall.
        size: new google.maps.Size(20, 32),
        // The origin for this image is 0,0.
        origin: new google.maps.Point(0,0),
        // The anchor for this image is the base of the flagpole at 0,32.
        anchor: new google.maps.Point(0, 32)
    };
    // Shapes define the clickable region of the icon.
    // The type defines an HTML &lt;area&gt; element 'poly' which
    // traces out a polygon as a series of X,Y points. The final
    // coordinate closes the poly by connecting to the first
    // coordinate.
    var shape = {
        coords: [1, 1, 1, 20, 18, 20, 18 , 1],
        type: 'poly'
    };

    var infowindow = new google.maps.InfoWindow();
    var marker, i;

    for (i = 0; i < tasks.length; i++) {
        var task = tasks[i];
        var myLatLng = new google.maps.LatLng(task.center_lat, task.center_lng);

        marker = new google.maps.Marker({
            position: myLatLng,
            animation: google.maps.Animation.DROP,
            map: map,
            icon: image,
            shape: shape,
            zIndex: i
        });

        // NOTE use tasks[i] explicitly
        google.maps.event.addListener(marker, 'click', (function(marker, i) {
                return function() {
                    infowindow.setContent(getTaskContent(task));
                    infowindow.open(map, marker);
                }
            })(marker, i));

        var circleOptions = {
            strokeColor: '#F59000',
            strokeOpacity: 0.3,
            strokeWeight: 1,
            fillColor: '#F59000',
            fillOpacity: 0.2,
            map: map,
            center: myLatLng,
            radius: tasks.radius
        };
        var taskCircle = new google.maps.Circle(circleOptions);
    }
}

getTaskContent(task) {
	var content = '<a href="'
		+ tasks[i].img_uri
		+ '" target="_blank"><img src="'
		+ tasks[i].img_uri
		+ '" height="300" width="300"></a><form method="post" action="answer?task_id='
		+ task.id
		+ '" enctype="application/json"><input type="text" name="answer"><input type="submit" value="Answer"></form>';

	return content;
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

function errorCallback(error) {
	var errorMessage = getErrorMessage(error);

	if (error.TIMEOUT) {
		// Quick fallback when no suitable cached position exists.
		doFallback();
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

function doFallback() {
	// No fresh enough cached position available.
	// Fallback to a default position.
}

// current position of the user
function setCurrentPosition(pos) {
	var image = {
		url: 'static/image/pegman.png',
		size: new google.maps.Size(24, 24),
		origin: new google.maps.Point(0,0),
		anchor: new google.maps.Point(12, 24)
	};
	var shape = {
		coords: [1, 1, 1, 20, 18, 20, 18 , 1],
		type: 'poly'
	};
	currentPositionMarkerInfoWindow = new google.maps.InfoWindow({
		content: '<p>You are here and I know</p><p>where to find your sweet ass</p>'
	});
	currentPositionMarker = new google.maps.Marker({
		map: map,
		position: new google.maps.LatLng(
			pos.coords.latitude,
			pos.coords.longitude
		),
		icon: image,
		shape: shape,
		animation: google.maps.Animation.DROP,
		title: "Current Position"
	});
	google.maps.event.addListener(currentPositionMarker, 'click', function() {
		currentPositionMarkerInfoWindow.open(map, currentPositionMarker);
	});
	map.panTo(new google.maps.LatLng(
			pos.coords.latitude,
			pos.coords.longitude
		));
}

function displayAndWatch(position) {

	// set current position
	setCurrentPosition(position);

	// watch position
	watchCurrentPosition();
}

function watchCurrentPosition() {
	var positionTimer = navigator.geolocation.watchPosition(
		function (position) {
			setMarkerPosition(
				currentPositionMarker,
				position
			);
		},
		errorCallback,
		{
			timeout: 200,
			enableHighAccuracy: true,
			maximumAge: Infinity
		});
}

function setMarkerPosition(marker, position) {
	marker.setPosition(
		new google.maps.LatLng(
			position.coords.latitude,
			position.coords.longitude)
	);
}

function initLocationProcedure() {
	initializeMap();
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			displayAndWatch,
			locError,
			{
				timeout: 1000,
				enableHighAccuracy: true,
				maximumAge: Infinity
			});
	} else {
		// tell the user if a browser doesn't support this amazing API
		locError();
	}
}

// initialize with a little help of jQuery
$(document).ready(function() {
	initLocationProcedure();
});
