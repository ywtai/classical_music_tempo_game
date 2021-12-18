var vid = document.getElementById("game_video");
var timer = null;
var point = 0;
var minutesLabel = document.getElementById("minutes");
var secondsLabel = document.getElementById("seconds");
var time_stamp = 0;
var turn = document.getElementById("turn");
var time_interval = 10;
var timing;
var index = 0;
var container = document.getElementById("game");

document.addEventListener("keydown", keyDown, false);

function keyDown(e) {
    if (e.keyCode ==37) //left arrow
    {
        send_keyboard_status('left');
    }
    else if (e.keyCode == 39) //right arrow
    {
        send_keyboard_status('right');
    }
}

function hide_ready() {
	document.getElementById("start").style.display="none";
    document.getElementById("ready").style.display="none";
    document.getElementById("game").style.display="block";
    vid.style.display="block";
}

function game_end() {
    document.getElementById("game_end").style.display="block";
    document.getElementById("game").style.display="none";
    vid.style.display="none";
    $('#end_score').html("SCORE : " + point);
}

function play_vid() {
    vid.play();
}

function get_game_timing() {
    $.ajax({
        url: "/get_game_timing",
        type: "get",
        data: {},
        success: function(response) {
            timing=response;
        },
        error: function(xhr) {
        }
    });
}

function start_game() {
    if (timer == null) {
        get_game_timing()
        play_vid();
        hide_ready();
        $.ajax({
            url: "/video_time",
            type: "get",
            data: {vid_duration: vid.duration},
            success: function(response) {
            },
            error: function(xhr) {
            }
        });
        timer = setInterval(setTime, time_interval);        
    }

    function setTime() {
        time_stamp = time_stamp+time_interval/1000;
        time_stamp = round_to_two(time_stamp);
        if (time_stamp > vid.duration){
            clearInterval(timer);
            game_end();
        }

        turn_timing = round_to_two(timing[index][0]-1);

        if (time_stamp === turn_timing) {
            if (timing[index][1] === "right")
                right_arrow_drop();
            else if (timing[index][1] === "left")
                left_arrow_drop();

            if (index < (Object.keys(timing).length)-1)
                index += 1;
        }
    }

    function round_to_two(num) {
        return +(Math.round(num + "e+2")  + "e-2");
    }
}

function send_keyboard_status(keyboard_status) {
    $.ajax({
        url: "/keyboard_status_get",
        type: "get",
        data: {jsdata: keyboard_status,
            time_stamp: time_stamp},
        success: function(response) {
            point = response['point'];
            $("#point").html("Score : " + point);
        },
        error: function(xhr) {
        }
    });
}

function submit_score(){
    $.ajax({
        url: "/submit_score",
        type: "get",
        data: {player_name: document.getElementById("player_name").value,
            point: point},
        success: function(response) {
        },
        error: function(xhr) {
        }
    });
}

function change_text_color() {
    if(document.getElementById("player_name").value=='Player Name'){
        document.getElementById("player_name").value=''
    };
    document.getElementById("player_name").style.color='black';
}

function right_arrow_drop() {
    var right_arrow = document.createElement("img");
    right_arrow.src = "/static/img/right.png";
    right_arrow.setAttribute("class", "right-arrow");

    container.appendChild(right_arrow);

    setTimeout(() => {
        container.removeChild(right_arrow);
    } , 1000)
}

function left_arrow_drop() {
    var right_arrow = document.createElement("img");
    right_arrow.src = "/static/img/right.png";
    right_arrow.setAttribute("class", "left-arrow");

    container.appendChild(right_arrow);

    setTimeout(() => {
        container.removeChild(right_arrow);
    } , 1000)
}