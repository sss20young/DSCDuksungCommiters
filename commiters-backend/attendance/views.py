from django.shortcuts import render, redirect
from django.views import generic
from .models import User, Repository, Commit
from django.http import JsonResponse
import json, requests
from django.core.serializers import json
from datetime import datetime, timedelta
from django.conf import settings

# Schedule - BackgroundScheduler(다수 수행)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import time

def get_commit_count_job():
    print("I'm working...", "| [time] "
          , str(time.localtime().tm_hour) + ":"
          + str(time.localtime().tm_min) + ":"
          + str(time.localtime().tm_sec))

    today = datetime(datetime.today().year, datetime.today().month, datetime.today().day) # 오늘
    yesterday = today - timedelta(1) # 어제(오늘-1)
    tomorrow = today + timedelta(1) # 내일(오늘+1)


    users = User.objects.all()

    for user in users:

        # 내 정보 추출 - Database
        mine_database = User.objects.get(userlogin = user.userlogin)

        # 내 Repository 정보 추출 - Github API
        repos = requests.get(
            'https://api.github.com/users/' + user.userlogin + '/repos',
            headers = { 'Authorization' : settings.GITHUB_OAUTH_TOKEN }
        )
        repos = repos.json()


        count = 0 # commit_count 초기화

        # Repository에 데이터 생성
        for repo in repos:
            if not Repository.objects.filter(name = repo['name'], user_user = User.objects.get(userlogin = user.userlogin)):
                Repository.objects.create(name = repo['name'], owner = repo['owner']['login'], user_user = User.objects.get(userlogin = user.userlogin))

            # 내 Commit 정보 추출 - Github API
            commits = requests.get(
                'https://api.github.com/repos/' + user.userlogin + '/' + repo['name'] + '/commits',
                headers = { 'Authorization' : settings.GITHUB_OAUTH_TOKEN }
            )
            commits = commits.json()
            

            # Commit에 데이터 생성 (하루 동안)
            for commit in commits:
                commit_date = commit['commit']['committer']['date']

                # TODO: detail한 부분 수정 필요
                # commit_date type 변환
                # 15시가 넘으면 날짜+1
                if (int(commit_date[11:13]) >= 15):
                    # 1,3,5,7,8,10,12월말인 경우
                    if (int(commit_date[8:10]) == 31):
                        if (int(commit_date[5:7]) == 1 or int(commit_date[5:7]) == 3 or int(commit_date[5:7]) == 5 or int(commit_date[5:7]) == 7 or int(commit_date[5:7]) == 8 or int(commit_date[5:7]) == 10 or int(commit_date[5:7]) == 12):
                            commit_date_month = int(commit_date[5:7])+1
                            commit_date_day = 1
                    elif (int(commit_date[8:10]) == 30):
                        # 2,4,5,9,11월말인 경우
                        if(int(commit_date[5:7]) == 2 or int(commit_date[5:7]) == 4 or int(commit_date[5:7]) == 6 or int(commit_date[5:7]) == 9 or int(commit_date[5:7]) == 11): # 월말인 경우
                            commit_date_month = int(commit_date[5:7])+1
                            commit_date_day = 1
                    else:
                        commit_date_month = int(commit_date[5:7])
                        commit_date_day = int(commit_date[8:10])+1
                    
                else: # 그렇지 않으면 그대로
                    commit_date_month = int(commit_date[5:7])
                    commit_date_day = int(commit_date[8:10])

                commit_date_year = int(commit_date[0:4])

                commit_date = datetime(commit_date_year, commit_date_month, commit_date_day)


                # committer filtering
                if ( commit['commit']['committer']['name'] == user.userlogin or commit['commit']['committer']['name'] == mine_database.name or commit['commit']['committer']['name'] == "GitHub"):
                    if (commit_date == today):
                        count = count + 1


        if Commit.objects.filter(user_user = User.objects.get(userlogin = user.userlogin), createdat__gte = today, createdat__lt = tomorrow): # 오늘 날짜가 있다면 수정
            commit_pre = Commit.objects.filter(user_user = User.objects.get(userlogin = user.userlogin), createdat__gte = today, createdat__lt = tomorrow)
            commit_pre.delete()
            Commit.objects.create(user_user = User.objects.get(userlogin = user.userlogin), commit_count = count)
        else: # 그렇지 않다면 생성
            Commit.objects.create(user_user = User.objects.get(userlogin = user.userlogin), commit_count = count)


# BackgroundScheduler 를 사용하면 start를 먼저 하고 add_job 을 이용해 수행할 것을 등록해준다.
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(get_commit_count_job, 'interval', hours=1, id="get_commit_count_job") # interval - 1시간 마다 실행




class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        start_day = datetime(2020, 11, 2) # 시작일 : 11월 2일
        today = datetime(datetime.today().year, datetime.today().month, datetime.today().day) # 오늘
        yesterday = today - timedelta(1) # 어제(오늘-1)
        tomorrow = today + timedelta(1) # 내일(오늘+1)

        until_now_attendance = {} # 지금까지 출석 현황
        today_attendance = {} # 오늘 출석 현황
        users = User.objects.all()
        for user in users:
            start_day = datetime(2020, 11, 2)
            list = [] # 리스트 초기화
            while start_day <= today:
                if start_day <= today:
                    if Commit.objects.filter(user_user = User.objects.get(userlogin = user.userlogin), createdat__gte = start_day, createdat__lt = start_day + timedelta(1)):
                        commits = Commit.objects.get(user_user = User.objects.get(userlogin = user.userlogin), createdat__gte = start_day, createdat__lt = start_day + timedelta(1))
                        list.append(commits.commit_count)

                        if (start_day == today):
                            today_attendance[user] = commits.commit_count
                    else:
                        list.append(0)

                    
                    start_day = start_day + timedelta(1)
                else:
                    break

            until_now_attendance[user] = list
            

        return render(request, 'home.html', { 'users' : users, 'until_now_attendance' : until_now_attendance, 'today_attendance' : today_attendance })
    
    def post(self, request, *args, **kwargs):

        # 내 정보 추출 - Github API
        mine_github = requests.get(
            'https://api.github.com/users/' + request.user.get_username(),
            headers = { 'Authorization' : settings.GITHUB_OAUTH_TOKEN }
        )
        mine_github = mine_github.json() # json 형식에서 데이터 추출
        

        # User(Attendance)에 데이터 생성
        if not User.objects.filter(userlogin = request.user.get_username()):
            User.objects.create(userlogin = mine_github['login'], name = mine_github['name'], profile = mine_github['avatar_url']) 


        # 내 정보 추출 - Database
        mine_database = User.objects.get(userlogin = request.user.get_username())


        # 내 Repository 정보 추출 - Github API
        repos = requests.get(
            'https://api.github.com/users/' + request.user.get_username() + '/repos',
            headers = { 'Authorization' : settings.GITHUB_OAUTH_TOKEN }
        )
        repos = repos.json()


        # Repository에 데이터 생성
        for repo in repos:
            if not Repository.objects.filter(name = repo['name'], user_user = User.objects.get(userlogin = request.user.get_username())):
                Repository.objects.create(name = repo['name'], owner = repo['owner']['login'], user_user = User.objects.get(userlogin = request.user.get_username()))

        return redirect('/')

def about(request):
    return render(request, 'about.html')

def mypage(request):
    mine = User.objects.get(userlogin = request.user.get_username())
    repos = Repository.objects.filter(user_user = mine.user_id)
    return render(request, 'mypage.html', { 'mine' : mine, 'repos' : repos })
