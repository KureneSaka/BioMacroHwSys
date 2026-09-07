# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .utils import *
from BioMacroHwSys.utils import initialweek
from BioMacroHwSys.auth import must_change_password, pwd_url


def studentlogin(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("/")
    msg = {
        "err": checkerror(request.COOKIES.get("login_error")),
        "id": request.COOKIES.get("login_id"),
    }
    if not msg["id"]:
        msg["id"] = ""
    return render(request, "student/login.html", msg)


def _login_fail(sid: str, err: str) -> HttpResponseRedirect:
    ret = redirect("/student/")
    ret.set_cookie("login_error", err)
    ret.set_cookie("login_id", sid)
    return ret


def checklogin(request: HttpRequest):
    sid = (request.POST.get("id") or "").strip()
    pwd = request.POST.get("password") or ""
    if not sid.isdigit():
        return _login_fail(sid, "E1")
    try:
        user = User.objects.get(username=sid)
    except User.DoesNotExist:
        return _login_fail(sid, "E2")
    if user.is_staff:
        return _login_fail(sid, "E4")
    if authenticate(request, username=sid, password=pwd) is None:
        return _login_fail(sid, "E3")
    login(request, user)
    if must_change_password(user):
        ret = redirect(pwd_url(user))
    else:
        ret = redirect("/student/index")
    ret.set_cookie("week", initialweek())
    return ret
