from django.shortcuts import render, redirect
from django.views import generic
from .models import User, Repository, Commit
from django.http import JsonResponse
import json, requests
from django.core.serializers import json
from datetime import datetime, timedelta


class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        dict = {}
        users = User.objects.all()
        for user in users:
            if Commit.objects.filter(user_user = User.objects.get(userlogin = user.userlogin)):
                commits = Commit.objects.get(user_user = User.objects.get(userlogin = user.userlogin))
                print(commits)
                dict[user] = commits.commit_count

        return render(request, 'home.html', { 'users' : users, 'dict' : dict })
    
    def post(self, request, *args, **kwargs):

        today = datetime(datetime.today().year, datetime.today().month, datetime.today().day) # 오늘
        yesterday = today - timedelta(2) # 어제(오늘-1)
        tomorrow = today + timedelta(1) # 내일(오늘+1)


        # 내 정보 추출 - Github API
        mine_github = requests.get(
            'https://api.github.com/users/' + request.user.get_username(),
            headers = { 'Authorization' : 'token aecdcbe00d40a4e6f9023a4d3e255ba87039371d' }
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
            headers = { 'Authorization' : 'token aecdcbe00d40a4e6f9023a4d3e255ba87039371d' }
        )
        repos = repos.json()


        count = 0 # commit_count 초기화

        # Repository에 데이터 생성
        for repo in repos:
            if not Repository.objects.filter(name = repo['name'], user_user = User.objects.get(userlogin = request.user.get_username())):
                Repository.objects.create(name = repo['name'], owner = repo['owner']['login'], user_user = User.objects.get(userlogin = request.user.get_username()))

            # 내 Commit 정보 추출 - Github API
            commits = requests.get(
                'https://api.github.com/repos/' + request.user.get_username() + '/' + repo['name'] + '/commits',
                headers = { 'Authorization' : 'token aecdcbe00d40a4e6f9023a4d3e255ba87039371d' }
            )
            commits = commits.json()
            

            # Commit에 데이터 생성 (하루 동안)
            for commit in commits:
                commit_date = commit['commit']['committer']['date']
                commit_date = commit_date[0:10]
                commit_date = datetime.strptime(commit_date, '%Y-%m-%d') # str to datetime
                # TODO: 시간 재설정 필요

                # committer filtering
                if ( commit['commit']['committer']['name'] == request.user.get_username() or commit['commit']['committer']['name'] == mine_database.name ):
                    if commit_date >= today and commit_date < tomorrow: # TODO: today로 변경
                        print(commit['commit']['committer'])
                        count = count + 1
            
        print(count)

        if Commit.objects.filter(user_user = User.objects.get(userlogin = request.user.get_username()), createdat__lte = today, createdat__gt = tomorrow): # 오늘 날짜가 있다면 수정
            commit_change = Commit.objects.filter(user_user = User.objects.get(userlogin = request.user.get_username()), createdat__lte = today, createdat__gt = tomorrow)
            commit_change.commit_count = count
            commit_change.save()
        else: # 그렇지 않다면 생성
            Commit.objects.create(user_user = User.objects.get(userlogin = request.user.get_username()), commit_count = count)

        return redirect('/')

def about(request):
    return render(request, 'about.html')

def mypage(request):
    mine = User.objects.get(userlogin = request.user.get_username())
    repos = Repository.objects.filter(user_user = mine.user_id)
    return render(request, 'mypage.html', { 'mine' : mine, 'repos' : repos })