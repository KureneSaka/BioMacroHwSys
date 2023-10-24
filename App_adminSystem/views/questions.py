# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *

def display_all(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getallquestions().filter(week=week)
    originQuesList = sorted(list(quesList_raw),
                            key=lambda x: x.seconded-x.disliked, reverse=True)
    quesList = originQuesList.copy()
    _Setting = request.POST.getlist("Setting")
    if "I" not in _Setting:
        msg["Setting_I"] = True
        for i in originQuesList:
            if not i.visible:
                quesList.remove(i)

    msg["quesNum"] = quesList_raw.filter(visible=True).count()
    msg["questions"] = quesList2dict(quesList)
    msg["realquesnum"] = len(quesList)
    outputMsg(msg)
    return render(request, "admin/display_all.html", msg)


# def display_personal(request: HttpRequest):
########TODO########
#     hash, r = checkcookies(request)
#     if r:
#         return r
#     msg = {}
#     quesList = list(getmyquestions(hash))
#     msg["quesNum"] = len(quesList)
#     msg["questions"] = quesList2dict(quesList)
#     outputMsg(msg)
#     return render(request, "student/display_mine.html", msg)


