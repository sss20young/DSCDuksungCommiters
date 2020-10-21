from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from .models import User, Repository
from django.http import JsonResponse
import json, requests

class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        repository = Repository.objects.all()
        return render(request, 'home.html', { 'user' : user, 'repository' : repository })
    
    def post(self, request, *args, **kwargs):
        # User(Attendance)에 정보 생성하기
        if not User.objects.filter(userlogin = request.user.get_username()):
            user = requests.get('https://api.github.com/users/' + request.user.get_username())
            user = user.json()
            User.objects.create(userlogin = user['login'], name = user['name'], profile = user['avatar_url'])
        return redirect('/')

def about(request):
    return render(request, 'about.html')

def mypage(request):
    user = User.objects.get_object_or_404(userlogin = request.user.get_username())
    return render(request, 'mypage.html', { 'user' : user })