"""
URL configuration for BioMacroHwSys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from .views import login, index, questions, respond, export, manage_admin, manage_student, week

urlpatterns = [
    path('', login.adminlogin),
    path('login', login.checklogin),
    path('index', index.index),
    path('display_all', questions.display_all),
    path('respond', respond.respond),
    path('responding', respond.responding),
    path('export_all', export.export_all),
    path('manage_student', manage_student.manage_student),
    path('add_student', manage_student.add_student),
    path('modify_student', manage_student.modify_student),
    path('manage_admin', manage_admin.manage_admin),
    path('add_admin', manage_admin.add_admin),
    path('modify_admin', manage_admin.modify_admin),
    path('next_week', week.next_week),
    path('prev_week', week.prev_week),
    path('change_week', week.change_week),
]
