# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from .utils import *

def studentlogin(request: HttpRequest):
    msg = {}
    msg["err"] = checkerror(request.COOKIES.get("login_error"))
    msg["id"] = request.COOKIES.get("login_id")
    msg["hash"] = request.COOKIES.get("login_hash")
    if not msg["id"]:
        msg["id"] = ""
    if not msg["hash"]:
        msg["hash"] = ""
    if not request.COOKIES.get("is_login"):
        return render(request, "student/login.html", msg)
    else:
        return redirect("/")


def checklogin(request: HttpRequest):
    suc, e = checkhash(request.POST["id"], request.POST["hash"])
    ret: HttpResponseRedirect
    if suc:
        ret = redirect("/student/index")
        ret.delete_cookie("login_error")
        ret.delete_cookie("login_id")
        ret.delete_cookie("login_hash")
        ret.set_cookie("is_login", "S" + request.POST["hash"])
    else:
        ret = redirect("/student/")
        ret.set_cookie("login_error", e)
        ret.set_cookie("login_id", request.POST["id"])
        ret.set_cookie("login_hash", request.POST["hash"])
    return ret
