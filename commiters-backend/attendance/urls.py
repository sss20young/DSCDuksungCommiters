from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.Attendance.as_view(), name='attendance'), # 메인 페이지
    path('about/', views.about, name='about'),
    path('mypage/', views.mypage, name='mypage'), # My Page
]