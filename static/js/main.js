var role = undefined;
var map;
var currentPositionMarker, mrxPositionMarker;
var prevGeoSendTime = undefined;

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
        $.mobile.pageContainer.pagecontainer("change", "#correctAnswerPage", {transition:"slide"});
    } else {
        alert(data.msg);
    }   
}

function cancelButtonHandler(taskId) {
    return function() {
        if (confirm("Are you sure? You won't be able to get back to this task in the furute")) {
            $.ajax({
                type: "POST",
                url: "/api/task/pause",
                data: {id:taskId},
                    success: function(data) {
                        location.reload();
                    },
                dataType: "json"
            }); 
        }
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
                data: {id:taskId},
                success: takeTaskHandler,
                dataType: "json"
            });
        })

      } 
}

function handleTasks(data) {
    var activeTask = undefined;

    for (var i = 0; i < map.polygons.length; i++) {
        polygon = map.polygons[i];
        polygon.setOptions({map:null});   
    }

    data.sort(function(a,b) {
        return b.radius - a.radius;
    });

    console.log(data)
    for (i = 0; i < data.length; i++) {
        var taskId = data[i].id;

        var color;

        switch (data[i].status) {
            case "available": color = "#F59000"; break;
            case "active": color = "#CC0000"; break;
            case "solved": color = "#33CC33"; break;
        }

        var circle;
        if (data[i].status == "available") {
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
        

        if (data[i].status == "active") {
            activeTask = data[i];
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
                data: {id:activeTask.id, answer:answer},
                success: answerHandler,
                dataType: "json"
                }); 
        });

        $('#taskComment').text(activeTask.comment);
        if (activeTask.has_present == true) {
            $('#answerContinueButton').hide()
            $('#presentContinueButton').show()

            $('#presentIconLink').show()

            $('#presentComment').text(activeTask.present.comment);
            $('#presentImg').attr("src",activeTask.present.img_url);
        }


    }
}

function updateTasks() {
    $.ajax({
            url: "/api/task/list",
            dataType: "json",
            success: handleTasks
    });
}

function slideGameStatus() {
    $.ajax({
        url: "/api/game_status",
        dataType: "json",
        success: function(data){
            if (data.game_status == "active") {
                if ($.mobile.activePage.attr('id') != "mainPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"none"});
                }
            } else if (data.game_status == "new") {
                if ($.mobile.activePage.attr('id') != "startPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#startPage", {transition:"none"});
                }
            } else if (data.game_status == "finished") {
                if ($.mobile.activePage.attr('id') != "gameoverPage") {
                    $.mobile.pageContainer.pagecontainer("change", "#gameoverPage", {transition:"none"});
                }
            }
        }
    });
}

function updateStatusBar() {
    $.ajax({
            url: "/api/solved_cnt",
            dataType: "json",
            success: function(data){
                $('#solved_cnt').text(data.val)
            }
    });
}

function initWithLogin() {
    slideGameStatus()
    initWithLoginAndRole();
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
    updateStatusBar();
}
    
function init() {
    document.body.style.marginTop = "20px";

    $("#startButton").click(function() {
        $.post("/api/start_game", function(data) {
            if (data.status == "success") {
                $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"slide"});
                location.reload();
            } else {
                alert(data.msg);
            }
        });
    });

    $(".continue_button").click(function() {
        $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"none"});
        location.reload();   
    });

    $(".newgamebutton").click(function() {
        $.post("/api/make_newgame", function(data) {
            $.mobile.pageContainer.pagecontainer("change", "#mainPage", {transition:"none"});
            location.reload();
        });
    });

    initWithLogin();
}

$(document).ready(init);