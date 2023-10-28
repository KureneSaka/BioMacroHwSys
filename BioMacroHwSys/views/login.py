# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..utils import *


def loginIndex(request: HttpRequest):
    loginCookies = request.COOKIES.get("is_login")
    ret:HttpRequest
    if loginCookies:
        if loginCookies[0] == 'S':
            ret = redirect("student/index")
        elif loginCookies[0]=='A':
            ret = redirect("admin/index")
    else:
        ret = render(request, "login.html")
    if not request.COOKIES.get("week"):
        ret.set_cookie("week", initialweek())
    return ret
