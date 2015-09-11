var authToken = localStorage.getItem('authToken');
var role = undefined;
var map;
var currentPositionMarker, mrxPositionMarker;
var prevGeoSendTime = undefined;

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

function cancelButtonHandler(taskId) {
    return function() {
        if (confirm("Are you sure? You won't be able to get back to this task in the furute")) {
            $.ajax({
                type: "POST",
                url: "/api/task/cancel",
                data: {id:taskId, token: authToken},
                    success: function(data) {
                        location.reload();
                    },
                dataType: "json"
            }); 
        }
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

        $('#takeTaskButton').show()
        if (role == "mrx") {
            $('#takeTaskButton').text("Try")   
        } else {
            $('#takeTaskButton').text("Investigate")
        }
        
        $('#takeTaskButton').off('click').click(function() {
            $.ajax({
                type: "POST",
                url: "/api/task/take",
                data: {id:taskId, token: authToken},
                success: takeTaskHandler,
                dataType: "json"
            });
        })

      } 
}

function handleTasks(data) {
    var activeTask = undefined;
    var requestedTask = undefined;

    for (var i = 0; i < map.polygons.length; i++) {
        polygon = map.polygons[i];
        polygon.setOptions({map:null});   
    }

    data.sort(function(a,b) {
        return b.radius - a.radius;
    });

    console.log(data);

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

        var circle;
        if (data[i].task_status == "pending" || data[i].task_status == "requested") {
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
                fillOpacity: 0.2,
                click: taskCircleCallback(data[i].id)
            });   
        } else {
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
        

        if (data[i].task_status == "active") {
            activeTask = data[i];
        }
        if (data[i].task_status == "requested") {
            requestedTask = data[i];
        }
    }

    if (activeTask != undefined) {
        $('#taskTimerContainer').hide();
        $('#taskImgLink').show();
        $('#taskImg').attr("src",activeTask.img_url);
        $('#taskImgLink').attr("href",activeTask.img_url);
        $('#taskText').text(activeTask.text);
        $('#cancelButton').removeAttr("disabled")
        $('#cancelButton').off('click').click(cancelButtonHandler(activeTask.id));
        $('#answerButton').removeAttr("disabled")
        $('#answerButton').off('click').click(function() {
            var answer = $('#answerInput').val();
            $.ajax({
                type: "POST",
                url: "/api/task/answer",
                data: {id:activeTask.id, answer:answer, token: authToken},
                success: answerHandler,
                dataType: "json"
                }); 
        });
    }

    if (requestedTask != undefined) {

        $('#taskTimerContainer').show();
        $('#cancelButton').removeAttr("disabled")
        $('#cancelButton').off('click').click(cancelButtonHandler(requestedTask.id));
        $('#taskTimerDiv').countdown({
            until: requestedTask.remaining,
            compact:true,
            onExpiry: function() {location.reload()}});

    }

}

function updateTasks() {
    $.ajax({
            url: "/api/task/list",
            data: {token: authToken},
            dataType: "json",
            success: handleTasks
    });
}

function updateStatusBar() {
    $.ajax({
        url: "/api/game_status",
        data: {token: authToken},
        dataType: "json",
        success: function(data){
            if (data.game_status == "active") {
                $('#timerDiv').countdown({
                    until: data.remaining, 
                    compact:true,
                    onExpiry: function() {location.reload()}
                });
                $("#waitBar").hide();
            } else if (data.game_status == "mrx_active") {
                if (role != "mrx") {
                    $("#waitBar").show();
                }
                $('#timerDiv').text(data.remaining.toHHMMSS())
            } else if (data.game_status == "finished") {
                if ($.mobile.activePage.attr('id') == "mainPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#gameoverPage", {transition:"slide"});   
                }
            } else {
                if ($.mobile.activePage.attr('id') == "mainPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#soonPage");   
                }
            }

        }
    });

    $.ajax({
            url: "/api/gap",
            dataType: "json",
            data: {token: authToken},
            success: function(data){
                $('#gap').text(data.gap)
            }
    });
    $.ajax({
            url: "/api/delta",
            dataType: "json",
            data: {token: authToken},
            success: function(data){
                $('#delta').text(data.delta)
            }
    });
    $.ajax({
            url: "/api/hunt_status",
            dataType: "json",
            data: {token: authToken},
            success: function(data) {
                if (data.hunt_active) {
                    $('#mushHuntBar').show();
                    if (role != "mrx") {
                        if (mrxPositionMarker == undefined) {
                            mrxPositionMarker = createNewMarker(data.lat, data.lng, false, true);
                        } else {
                            mrxPositionMarker.setPosition(
                                new google.maps.LatLng(
                                    data.lat,
                                    data.lng)
                            );
                        }
                    }

                } else {
                    $('#mushHuntBar').hide();
                    if (mrxPositionMarker != undefined) {
                        mrxPositionMarker.setOptions({map:null});
                        mrxPositionMarker = undefined;
                    }
                }
            }
    });
}

function initWithLogin() {
    $.ajax({
        url: "/api/game_status",
        data: {token: authToken},
        dataType: "json",
        success: function(data){
            if (data.game_status == "finished") {
                if ($.mobile.activePage.attr('id') != "gameoverPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#gameoverPage", {transition:"slide"});   
                }
            } else if (data.game_status == "no") {
                if ($.mobile.activePage.attr('id') != "soonPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#soonPage");   
                }
            }

        }
    });

    $.ajax({
        type: "GET",
        url: "/api/role",
        data: {token:authToken},
        success: function(data) {
            if (data.status == "success") {
                role = data.role;
                initWithLoginAndRole();
            }
        },
        dataType: "json"
    }); 
}

function initWithLoginAndRole() {
    map = new GMaps({
            div: '#map-canvas',
            lat: 55.754365,
            lng: 37.620041,
            disableDefaultUI: true,
            zoomControl: true
            });

    updateTasks();
    setInterval(updateTasks, 30000);
    updateStatusBar();
    setInterval(updateStatusBar, 10000);

    if (role == "mrx") {
        $("#codeTabBtn").addClass("ui-state-disabled");
    }
    $('#codeButton').click(function() {
            $.ajax({
                type: "POST",
                url: "/api/submit_mrx_code",
                data: {code:$('#codeInput').val(), token:authToken},
                success: codeHandler,
                dataType: "json"
                }); 
        });

    watchCurrentPosition();
}

function watchCurrentPosition() {
    var positionTimer = navigator.geolocation.watchPosition(
        function (position) {

            var currTime = (new Date()).getTime();

            if (prevGeoSendTime == undefined || currTime - prevGeoSendTime > 10000) {
                $.ajax({
                    type: "POST",
                    url: "/api/send_location",
                    data: {lat: position.coords.latitude, lng: position.coords.longitude, token:authToken},
                    dataType: "json"
                });  
                
                prevGeoSendTime = currTime;  
            }

            if (currentPositionMarker == undefined) {
                currentPositionMarker = createNewMarker(position.coords.latitude, position.coords.longitude, true, role=="mrx");
            } else {
                currentPositionMarker.setPosition(
                    new google.maps.LatLng(
                        position.coords.latitude,
                        position.coords.longitude)
                );
            }
        },
        function(error) {alert(getErrorMessage(error))},
        {
            timeout: 10000,
            enableHighAccuracy: true,
            maximumAge: 1000
        });
    
    // setTimeout( function() { navigator.geolocation.clearWatch( positionTimer ); }, 5000 );
}

function createNewMarker(lat, lng, isPanTo, isMrx) {
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
        icon: image
    });
        
    if (isPanTo) {
        map.panTo(new google.maps.LatLng(
                lat,
                lng
            ));
    }

    return marker;  
}
    
function init() {
    document.body.style.marginTop = "20px";

    var soonImgUrl;
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
        soonImgUrl = "/static/image/soon.jpg"
    } else {
        soonImgUrl = "/static/image/soonBig.jpg"
    }
    $("#soonPage").css('background-image', 'url(' + soonImgUrl + ')')

    $(".logoutButton").click(function() {
        localStorage.removeItem('authToken');   
        
        location.reload(); 
    })

    $("#loginButton").click(function() {
            var u = $("#username").val();
            var p = $("#password").val();
            
            if(u != '' && p!= '') {
                $.post("/auth/login", {username:u,password:p}, function(data) {
                    if (data.status == "success") {
                        localStorage.setItem('authToken', data.token);
                        authToken = data.token;
                        $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"slide"});

                        initWithLogin();
                    } else {
                        alert("Wrong username or password");
                    }
                });
            }
        });

    $("#regButton").click(function() {
        var u = $("#regusername").val();
        var ph = $("#regphone").val();
        var p = $("#regpassword").val();

        $.post("/auth/register", {username:u,password:p,phone:ph}, function(data) {
                if (data.status == "success") {
                    localStorage.setItem('authToken', data.token);
                    authToken = data.token;
                    $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"slide"});

                    initWithLogin();
                } else {
                    alert("Registration failed");
                }
        });

    });

    if (authToken != undefined) {
        initWithLogin();
    } else {
        $.mobile.pageContainer.pagecontainer("change", "#loginPage", {transition:"slide"});
    }
}

$(document).ready(init);