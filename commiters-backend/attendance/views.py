from django.shortcuts import render, redirect
from django.views import generic
from .models import User, Repository, Commit
from django.http import JsonResponse
import json, requests
from django.core.serializers import json
from datetime import datetime, timedelta


class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        return render(request, 'home.html', { 'users' : users })
    
    def post(self, request, *args, **kwargs):

        today = datetime(datetime.today().year, datetime.today().month, datetime.today().day) # 오늘
        yesterday = today - timedelta(1) # 어제(오늘-1)
        tomorrow = today + timedelta(1) # 내일(오늘+1)


        # 내 정보 추출 - Github API
        mine_github = requests.get(
            'https://api.github.com/users/' + request.user.get_username(),
            headers = { 'Authorization' : 'token d18ecd3db8dd947f732fd89e92d650363a47c1dd' }
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
            headers = { 'Authorization' : 'token d18ecd3db8dd947f732fd89e92d650363a47c1dd' }
        )
        repos = repos.json()


        # Repository에 데이터 생성
        for repo in repos:
            if not Repository.objects.filter(name = repo['name'], user_user = User.objects.get(userlogin = request.user.get_username())):
                Repository.objects.create(name = repo['name'], owner = repo['owner']['login'], user_user = User.objects.get(userlogin = request.user.get_username()))

            # 내 Commit 정보 추출 - Github API
            commits = requests.get(
                'https://api.github.com/repos/' + request.user.get_username() + '/' + repo['name'] + '/commits',
                headers = { 'Authorization' : 'token d18ecd3db8dd947f732fd89e92d650363a47c1dd' }
            )
            commits = commits.json()
            
            # Commit에 데이터 생성 (하루 동안)
            for commit in commits:
                commit_date = commit['commit']['committer']['date']
                commit_date = commit_date[0:10]
                commit_date = datetime.strptime(commit_date, '%Y-%m-%d') # str to datetime
                # TODO: 시간 재설정 필요
                # TODO: user_user 한번 더 filtering
                if commit_date >= yesterday and commit_date < tomorrow: # TODO: today로 변경
                    print(commit['commit']['committer'])
                    Commit.objects.create(repository_repository = Repository.objects.get(name = repo['name']), user_user = User.objects.get(userlogin = request.user.get_username()))>

        return redirect('/')

def about(request):
    return render(request, 'about.html')

def mypage(request):
    mine = User.objects.get(userlogin = request.user.get_username())
    repos = Repository.objects.filter(user_user = mine.user_id)
    return render(request, 'mypage.html', { 'mine' : mine, 'repos' : repos })