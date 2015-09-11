var map;
function initializeMap()
{
	var lat = 55.754365;
	var lng = 37.620041;

	map = new GMaps({
            div: '#map-canvas',
            lat: lat,
            lng: lng
        });
}

function createNewMarker(lat, lng, isMrx, time) {
    if (isMrx) {
        imgUrl = 'static/image/pegman_mrx.png';
    } else {
        imgUrl = 'static/image/pegman_sherlock.png';
    }
    
    var image = {
        url: imgUrl,
        size: new google.maps.Size(40, 50),
        origin: new google.maps.Point(0,0),
        anchor: new google.maps.Point(20, 25)
    };

    var marker = map.addMarker({
        lat: lat,
        lng: lng,
        icon: image,
        infoWindow: {content: time}

    });

    return marker;  
}

function updateMarkersCallback(data) {
	map.removeMarkers();
	console.log(data)
	
	for (var i = data.length - 1; i >= 0; i--) {
		createNewMarker(data[i].lat, data[i].lng, data[i].role == "mrx", data[i].time);	
	};	
 }

function updateMarkers() {
	$.ajax({
            url: "/api/all_locations",
            dataType: "json",
            success: updateMarkersCallback
    });
}

var main = function () {
	console.log("hi")
	initializeMap();

	updateMarkers();
	setInterval(updateMarkers, 10000);
}
$(document).ready(main);