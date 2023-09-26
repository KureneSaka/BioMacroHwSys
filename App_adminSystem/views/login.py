# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators import csrf
from . import utils

def adminlogin(request: HttpRequest):
    if not request.COOKIES.get("is_login"):
        return render(request, "admin/login.html")
    else:
        return redirect("/")
