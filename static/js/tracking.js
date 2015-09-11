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

function createNewMarker(lat, lng, isMrx, time, username) {
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
        infoWindow: {content: "<p>" + time + "</p>" + username}

    });

    return marker;  
}

function updateMarkersCallback(data) {
	map.removeMarkers();
	console.log(data)
	
	for (var i = data.length - 1; i >= 0; i--) {
		createNewMarker(data[i].lat, data[i].lng, data[i].role == "mrx", data[i].time, data[i].username);	
	};	
 }

function updateMarkers() {
	$.ajax({
            url: "/api/all_locations",
            dataType: "json",
            success: updateMarkersCallback
    });

    $.ajax({
            url: "/api/task/list_crimes",
            dataType: "json",
            success: handleTasks
    });
}

function handleTasks(data) {

    for (var i = 0; i < map.polygons.length; i++) {
        polygon = map.polygons[i];
        polygon.setOptions({map:null});   
    }

    for (i = 0; i < data.length; i++) {
        var taskId = data[i].id;

        var color;

        switch (data[i].status) {
            case "commited": color = "#F59000"; break;
            case "not_commited": color = "#666666"; break;
            case "solved": color = "#33CC33"; break;
        }

        console.log(color);

		circle = map.drawCircle({
            id: data[i].id,
            lat: data[i].lat,
            lng: data[i].lng,
            radius: data[i].radius,
            zIndex: i,
            strokeColor: color,
            strokeOpacity: 0.5,
            strokeWeight: 1,
            fillColor: color,
            fillOpacity: 0.2
        });   
    }

  }

var main = function () {
	console.log("hi")
	initializeMap();

	updateMarkers();
	setInterval(updateMarkers, 10000);
}
$(document).ready(main);