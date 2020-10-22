from django.shortcuts import render, redirect
from django.views import generic
from .models import User, Repository, Commit
from django.http import JsonResponse
import json, requests
from django.core.serializers import json


class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        repository = Repository.objects.all()
        return render(request, 'home.html', { 'users' : users, 'repository' : repository })
    
    def post(self, request, *args, **kwargs):
        # User(Attendance)에 정보 생성하기
        if not User.objects.filter(userlogin = request.user.get_username()):
            users = requests.get('https://api.github.com/users/' + request.user.get_username())
            users = users.json()
            User.objects.create(userlogin = users['login'], name = users['name'], profile = users['avatar_url'])
            

        users = requests.get('https://api.github.com/users/' + request.user.get_username(),
            headers = {'Authorization': 'token 74344d37dd9b748d29d96db7e6e71d4b673377ca'})
        users = users.json()
        # Repository에 정보 생성하기
        user = User.objects.get(userlogin = request.user.get_username())
        print(user.user_id)
    
        repos = requests.get('https://api.github.com/users/' + request.user.get_username() + '/repos',
            headers = {'Authorization': 'token 74344d37dd9b748d29d96db7e6e71d4b673377ca'})
        repos = repos.json()
        # for repo in repos:
            # Repository.objects.create(name = repo['name'], owner = repo['owner']['login'], user_user = User.objects.get(userlogin = request.user.get_username()))

        repos = Repository.objects.filter(user_user = User.objects.get(userlogin = request.user.get_username()))

        print(repos)

        for repo in repos:
            commits = requests.get('https://api.github.com/repos/' + request.user.get_username() + '/' + repo.name +'/commits',
            headers = {'Authorization': 'token 74344d37dd9b748d29d96db7e6e71d4b673377ca'})
            commits = commits.json()
            print(repo.repository_id)
            for commit in commits:
                # print(commit[2][1][2])
                Commit.objects.create(
                    repository_repository = Repository.objects.get(repository_id = repo.repository_id),
                    user_user = User.objects.get(userlogin = user),
                    # createdat = commit['commit']['committer']['date']
                )    

        return redirect('/')

def about(request):
    return render(request, 'about.html')

def mypage(request):
    users = User.objects.get(userlogin = request.user.get_username())
    repos = Repository.objects.filter(user_user = users.user_id)
    return render(request, 'mypage.html', { 'users' : users, 'repos' : repos })