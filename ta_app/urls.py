"""
URL configuration for ta_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from ta_scheduler import views
from ta_scheduler.views import (UserListView, UserCreateView, UserUpdateView, UserDetailView, user_delete,
                                PublicProfileView, PrivateProfileView, EditPublicProfileView, PrivateProfileUpdateView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.loginUser, name = "login"),
    path('home/', views.home, name = "home"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('HomePageTemplate/', views.HomePageTemplate, name = 'HomePageTemplate'),
    path('home/Courses.html', views.courses, name = 'courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/view/', UserDetailView.as_view(), name='user-view'),
    path('users/<int:pk>/confirm_delete/', UserDetailView.as_view(), name='user-confirm-delete'),
    path('users/<int:pk>/delete/', user_delete, name='user-delete'),
    path('users/Courses.html', views.courses, name = 'courses'),
    path('users/Profiles.html', UserListView.as_view(), name = 'user-list'),
    path('home/Home.html', views.home, name = 'home'),
    path('home/Profiles.html', UserListView.as_view(), name = 'user-list'),
    path('profile/<str:username>/public/', PublicProfileView.as_view(), name='public_profile'),
    path('profile/<str:username>/private/', PrivateProfileView.as_view(), name='private_profile'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/edit/', EditPublicProfileView.as_view(), name='edit_public_profile'),

    path('profile/private/edit/', PrivateProfileUpdateView.as_view(), name='edit_private_profile'),
]
