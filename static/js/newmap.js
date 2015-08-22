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
}

function initLocationProcedure() {
	initializeMap();
}

// initialize with a little help of jQuery
$(document).ready(function() {
	initLocationProcedure();
});
