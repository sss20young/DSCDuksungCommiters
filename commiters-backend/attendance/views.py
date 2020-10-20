from django.shortcuts import render
from django.views import generic
from .models import User, Repository
from django.http import JsonResponse
import json

class Attendance(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        repository = Repository.objects.all()
        return render(request, 'home.html', { 'user' : user, 'repository' : repository })

def about(request):
    return render(request, 'about.html')

def mypage(request):
    user = User.objects.get(name = request.user.get_username())
    return render(request, 'mypage.html', { 'user' : user })