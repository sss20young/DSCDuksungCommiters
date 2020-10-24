google.charts.load('current', {'packages':['corechart']});

var progress_bar = new ProgressBar.Circle();

var username=[];
var userid=[];
var cc=[];
var formatted_dates=[];
var all_dates=[];
const total_days=14;

const today= new Date();
const yesterday = new Date(new Date().setDate(new Date().getDate()-1));
const start_day = new Date(2020, 11, 2);
const last_day = new Date(2020, 11, 15);
var progressed_day;

let now = new Date();
let year = now.getFullYear();
let month = now.getMonth();
let date = now.getDate();
var event = new Date(year,month,date);
console.log(event);


// 출석부 날짜 범위

function resolveCalendar() {
    for (let date = new Date(start_day); date <= last_day; new Date(date.setDate(date.getDate() + 1))) {
        all_dates.push(moment(date).format("MM/DD"));
    }

    for (let date = new Date(start_day); date <= yesterday; new Date(date.setDate(date.getDate() + 1))) {
        formatted_dates.push(moment(date).format("YYYY-MM-DD"));
    }
    
    //console.log(formatted_dates.length);
    return formatted_dates;
}

async function setCalendar() {
    const result = await resolveCalendar();
    progressed_day = result.length;
}

setCalendar();

//사용자, 커밋 수 가져오기
new Promise(function (res, rej) {
    setTimeout(function() {
        var arr = Array.from(document.getElementsByClassName("nickname"));
        for (var i = 0; i < arr.length; i++) {
            username.push(arr[i].getAttribute('pk'));
        }
        res(username);
    }, 10);
}).then(function () {
    new Promise(function (res, rej) {
        var arr = Array.from(document.getElementsByClassName("nickname"));
        for (var i = 0; i < arr.length; i++) {
            userid.push(arr[i].getAttribute('id'));
        }
        res(userid);
    });
}).then (function () {
    new Promise(function (resolve, rej) {

    //유저 단위
    for(let i = 0; i < username.length; i++) {
        axios.get('https://api.github.com/users/'+username[i]+'/repos', {
        headers: {
            'Authorization': 'token 74344d37dd9b748d29d96db7e6e71d4b673377ca'
        }
        }).then(res => {
            let sum=0;

            // 저장소 단위
            for(var t=0;t< (res.data).length ; t++) {
                // 날짜 있었던 자리
                // GET /repos/:owner/:repo/commits
                // https://api.github.com/repos/sss20young/DSCDuksungCommiters/commits
                axios.get('https://api.github.com/repos/'+((res.data)[t].owner).login+'/'+(res.data)[t].name+'/commits', {
                params: { since: event.toISOString() },
                headers: {
                    'Authorization': 'token 74344d37dd9b748d29d96db7e6e71d4b673377ca'
                }
                }).then(res=>{
                    let commit_cnt = (res.data).length;
                    sum+=commit_cnt;
                    cc[i]=sum;
                    console.log(cc[i]);
                });
            }
        });
        }
        resolve(cc);
    }).then(function() {
        setTimeout(function() {
            var cnt=0;

            let today_attendance_html;

            for(var u=0;u<username.length;u++){
                if(cc[u]!==0){
                    cnt+=1;
                }
                //오늘 출석했다면 배경칠하기
                if(cc[u]>0){
                    console.log('.users:nth-child('+u+')');
                    $('.user-profile:nth-child('+(u+1)+')').css('background-color', "#b70050");

                }
            }

            //오늘의 출석부
            today_attendance_html+= `<td>${month+1}/${date}</td>`;
            for(var g=0;g<username.length;g++){
                if(cc[g]==0) {
                    today_attendance_html+=`<td>X</td> `;
                }

                else {
                    today_attendance_html+=`<td>O</td> `;
                }
            }

            $("#attendees").html(today_attendance_html);


            let progress_rate = Math.round(progressed_day/total_days*100);

            google.charts.setOnLoadCallback(draw_progress(progress_rate));
            google.charts.setOnLoadCallback(draw_attend_noshow(username.length, cnt));

        }, 3500);
    });
});

// 진행률 그래프
function draw_progress(progress) {
    let html = `<h5 class="text-center">총 ${all_dates.length}일 중 ${formatted_dates.length}일 진행</h5><br>`;

    let progress_rate = progress;

    progress_bar = new ProgressBar.Circle('#circle-progress', {
        color: '#aaa',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 4,
        easing: 'easeInOut',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: { color: '#b70050', width: 3 },
        to: { color: '#b70050', width: 5 },
        // Set default step function for all animate calls
        step: function(state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);

            var value = Math.round(circle.value() * 100);
            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value+"%");
            }

        }
    });
    progress_bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    progress_bar.text.style.fontSize = '2rem';
    progress_bar.text.style.color = "#b70050";

    progress_bar.animate(progress_rate/100);  // Number from 0.0 to 1.0

    $("#progress").html(html);

}

//오늘의 출석률 그래프
function draw_attend_noshow(total_user, today_count) {
    let html = `<h5 class="text-center">총 ${total_days}일 중 ${progressed_day}일 진행</h5>`;

    let total_attendance_rate = Math.round(today_count / total_user * 100 );

    let attend_noshow_html =`<br><h5 class ="text-center">오늘의 전체 출석률 ${total_attendance_rate}%</h5>`

    var bar = new ProgressBar.Line(container, {
        strokeWidth: 4,
        easing: 'easeInOut',
        duration: 1400,
        color: '#FFEA82',
        trailColor: '#eee',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '20px'},
        from: {color: '#b70050'},
        to: {color: '#b70050'},
        step: (state, bar) => {
            bar.path.setAttribute('stroke', state.color);
        }
    });

    bar.animate(total_attendance_rate/100);  // Number from 0.0 to 1.0

    $("#attend_noshow_div").html(attend_noshow_html);
}