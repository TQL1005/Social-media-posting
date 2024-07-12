from django.urls import path, include
from .views import CustomLoginView, RegisterPage, Main
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # path('', views.home),
    # path('register/', views.register),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('register/', RegisterPage.as_view(), name="register"),
    path('logout/', LogoutView.as_view(next_page='login'), name="logout"),
    path('', Main.as_view(), name="main"),
    path('accounts/', include('allauth.urls')),

]
