var map,
	marker

function initializeMap(pos)
{
	map = new google.maps.Map(document.getElementById('map-canvas'), {
		zoom: 15,
		center: pos,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		disableDefaultUI: true,
		zoomControl: true,
		zoomControlOptions: {
			style: google.maps.ZoomControlStyle.SMALL,
			position: google.maps.ControlPosition.RIGHT_BOTTOM
		}
	});

	marker = new google.maps.Marker({
            position: pos,
            draggable: true,
            map: map
    });

    google.maps.event.addListener(marker, 'dragend', function () {
            $("#latitude").val(marker.getPosition().lat());
            $("#longitude").val(marker.getPosition().lng());

            map.panTo(marker.getPosition());
    });
}

function processGeoposition(position)
{
	var currpos = new google.maps.LatLng(
			position.coords.latitude,
			position.coords.longitude
	);

	$("#latitude").val(currpos.lat());
	$("#longitude").val(currpos.lng());

	initializeMap(currpos)
}

function processFailGeoposition(position)
{
	var currpos = new google.maps.LatLng(
			55.754365,
			37.620041
	);

	$("#latitude").val(currpos.lat());
	$("#longitude").val(currpos.lng());

	initializeMap(currpos)
}

var main = function () {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			processGeoposition,
			processFailGeoposition,
			{
				timeout: 1000,
				maximumAge: Infinity
			});
	}


	$('#myForm').ajaxForm(function() { 
    	alert("OK"); 
    	location.reload();
    });
}

$(document).ready(main);