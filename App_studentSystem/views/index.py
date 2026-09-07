# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def index(request:HttpRequest):
    sid,r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    msg["StuName"] = name_of(sid)
    msg["StuId"] = sid
    msg["StuQuesNum"] = hash2quesnum(sid,week)
    msg["StuRespNum"] = hash2respnum(sid,week)
    return render(request, "student/index.html", msg)
