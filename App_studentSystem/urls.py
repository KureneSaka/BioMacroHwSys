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
from .views import evaluate, login, index, questions, submit, export, respond, respond_evaluate, week

urlpatterns = [
    path('', login.studentlogin),
    path('login', login.checklogin),
    path('index', index.index),
    path('submit',submit.submit),
    path('display_all',questions.display_all),
    path('display_mine',questions.display_mine),
    path('evaluate', evaluate.evaluate),
    path('evaluating', evaluate.evaluating),
    path('respond_evaluate', respond_evaluate.respond_evaluate),
    path('respond_evaluate_ing', respond_evaluate.respond_evaluate_ing),
    path('respond', respond.respond),
    path('responding', respond.responding),
    path('export_all', export.export_all),
    path('export_mine', export.export_mine),
    path('next_week', week.next_week),
    path('prev_week', week.prev_week),
    path('change_week', week.change_week),

]
