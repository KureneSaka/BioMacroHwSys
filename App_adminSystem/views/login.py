# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from .utils import *

def adminlogin(request: HttpRequest):
    msg, week = checkweek(request)
    msg["err"] = checkerror(request.COOKIES.get("login_error"))
    msg["hash"] = request.COOKIES.get("login_hash")
    if not msg["hash"]:
        msg["hash"] = ""
    if not request.COOKIES.get("is_login"):
        return render(request, "admin/login.html", msg)
    else:
        return redirect("/")


def checklogin(request: HttpRequest):
    suc, e = checkhash(request.POST["hash"])
    ret: HttpResponseRedirect
    if suc:
        ret = redirect("/admin/index")
        ret.delete_cookie("login_error")
        ret.delete_cookie("login_hash")
        ret.set_cookie("is_login", "A" + request.POST["hash"])
    else:
        ret = redirect("/admin/")
        ret.set_cookie("login_error", e)
        ret.set_cookie("login_hash", request.POST["hash"])
    return ret
