# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect


def loginIndex(request: HttpRequest):
    loginCookies = request.COOKIES.get("is_login")
    if loginCookies:
        if loginCookies[0] == 'S':
            return redirect("student/index")
        elif loginCookies[0]=='A':
            return redirect("admin/index")
    return render(request, "login.html")
