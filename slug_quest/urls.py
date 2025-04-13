from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path("sign-in-callback", views.sign_in_callback, name="sign_in_callback"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('main/', views.main, name='main')
]