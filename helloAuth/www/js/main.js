var authToken = "o2scv5nn7yq50dccovgnamxe9iubuqno"; //localStorage.getItem('authToken');
var apiDomain = "http://127.0.0.1:8080";
var map;

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

function cancelButtonHandler(taskId) {
    return function() {
        if (confirm("Are you sure? You won't be able to get back to this task in the furute")) {
            $.ajax({
                type: "POST",
                url: apiDomain + "/api/task/cancel",
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
        $('#takeTaskButton').text("Investigate " + taskId)
        $('#takeTaskButton').off('click').click(function() {
            $.ajax({
                type: "POST",
                url: apiDomain + "/api/task/take",
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
        $('#taskTimerDiv').hide();
        $('#taskImgLink').show();
        $('#taskImg').attr("src",activeTask.img_url);
        $('#taskImgLink').attr("href",activeTask.img_url);
        $('#cancelButton').removeAttr("disabled")
        $('#cancelButton').off('click').click(cancelButtonHandler(activeTask.id));
        $('#answerButton').removeAttr("disabled")
        $('#answerButton').off('click').click(function() {
            var answer = $('#answerInput').val();
            $.ajax({
                type: "POST",
                url: apiDomain + "/api/task/answer",
                data: {id:activeTask.id, answer:answer, token: authToken},
                success: answerHandler,
                dataType: "json"
                }); 
        });
    }

    if (requestedTask != undefined) {

        $('#taskTimerDiv').show();
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
            url: apiDomain + "/api/task/list",
            data: {token: authToken},
            dataType: "json",
            success: handleTasks
    });
}

function updateStatusBar() {
    $.ajax({
        url: apiDomain + "/api/game_status",
        data: {token: authToken},
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
            url: apiDomain + "/api/gap",
            dataType: "json",
            data: {token: authToken},
            success: function(data){
                $('#gap').text(data.gap)
            }
    });
    $.ajax({
            url: apiDomain + "/api/delta",
            dataType: "json",
            data: {token: authToken},
            success: function(data){
                $('#delta').text(data.delta)
            }
    });
    $.ajax({
            url: apiDomain + "/api/hunt_status",
            dataType: "json",
            data: {token: authToken},
            success: function(data) {
                if (data.hunt_active) {
                    $('.hunt-bar').show();
                }
            }
    });
}

function initWithLogin() {
    map = new GMaps({
            div: '#map-canvas',
            lat: 55.754365,
            lng: 37.620041
            });

    updateTasks();
    updateStatusBar();

    $('#codeButton').click(function() {
            $.ajax({
                type: "POST",
                url: apiDomain + "/api/submit_mrx_code",
                data: {code:$('#codeInput').val(), token:authToken},
                success: codeHandler,
                dataType: "json"
                }); 
        });
}

var app = {

    initialize: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
    },
    
    onDeviceReady: function() {
        console.log(authToken);

        document.body.style.marginTop = "20px";
        if (authToken != undefined) {
            initWithLogin();
        } else {
            $.mobile.pageContainer.pagecontainer("change", "#loginPage", {transition:"slide"});

            $("#loginForm").on("submit",function(e) {
            
                $("#submitButton",this).attr("disabled","disabled");
                var u = $("#username", this).val();
                var p = $("#password", this).val();

                if(u != '' && p!= '') {
                    $.post(apiDomain + "/auth/login", {username:u,password:p}, function(data) {
                        if (data.status == "success") {
                            localStorage.setItem('authToken', data.token);
                            authToken = data.token;
                            $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"slide"});

                            initWithLogin();
                        }
                    });
                }
            });
        }
    }
};

app.initialize();