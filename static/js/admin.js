var map,
	marker

function initializeMap()
{
	var lat = 55.754365;
	var lng = 37.620041;

	map = new GMaps({
            div: '#map-canvas',
            lat: lat,
            lng: lng
        });

	marker = map.addMarker({
		lat: lat,
        lng: lng,
        draggable: true,
        dragend: function(pos) {
         	$("#latitude").val(pos.latLng.lat());
            $("#longitude").val(pos.latLng.lng());

            map.panTo(pos.latLng);	
         }
	});
}

var main = function () {
	initializeMap();

	$('#myForm').ajaxForm(function() { 
    	alert("OK"); 
    	location.reload();
    });

    $("#radius").on('input', function() {
    	for (var i = 0; i < map.polygons.length; i++) {
        	polygon = map.polygons[i];
        	polygon.setOptions({map:null});   
    	}

    	var lat = marker.getPosition().lat();
    	var lng = marker.getPosition().lng();

    	var latLng = new google.maps.LatLng(
			lat, lng
		);

    	var circle = map.drawCircle({
            strokeColor: '#F59000',
            strokeOpacity: 0.3,
            strokeWeight: 1,
            fillColor: '#F59000',
            fillOpacity: 0.2,
            lat: lat,
            lng: lng,
            radius: parseInt($("#radius").val())
        });
    });
}

$(document).ready(main);