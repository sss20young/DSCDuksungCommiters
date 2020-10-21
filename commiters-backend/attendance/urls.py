from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.Attendance.as_view(), name='attendance'), # 메인 페이지
    path('about/', views.about, name='about'), # About Commiters
    path('mypage/', views.mypage, name='mypage'), # My Page
    path('attend', views.Attendance.as_view(), name='attend'), # 참여하기
]