# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators import csrf
from .utils import *


def studentlogin(request: HttpRequest):
    if not request.COOKIES.get("is_login"):
        return render(request, "student/login.html")
    else:
        return redirect("/")


def checklogin(request: HttpRequest):
    suc, e = checkhash(request.POST["id"], request.POST["hash"])
    print(suc)
    print(e)
    return redirect("/")
