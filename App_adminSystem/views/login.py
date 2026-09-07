# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .utils import *
from BioMacroHwSys.auth import must_change_password, pwd_url


def adminlogin(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("/")
    msg = {
        "err": checkerror(request.COOKIES.get("login_error")),
        "username": request.COOKIES.get("login_username"),
    }
    if not msg["username"]:
        msg["username"] = ""
    return render(request, "admin/login.html", msg)


def _login_fail(username: str, err: str) -> HttpResponseRedirect:
    ret = redirect("/admin/")
    ret.set_cookie("login_error", err)
    ret.set_cookie("login_username", username)
    return ret


def checklogin(request: HttpRequest):
    username = (request.POST.get("username") or "").strip()
    pwd = request.POST.get("password") or ""
    if not username:
        return _login_fail(username, "E1")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return _login_fail(username, "E2")
    if not user.is_staff:
        return _login_fail(username, "E4")
    if authenticate(request, username=username, password=pwd) is None:
        return _login_fail(username, "E3")
    login(request, user)
    if must_change_password(user):
        ret = redirect(pwd_url(user))
    else:
        ret = redirect("/admin/index")
    return ret
