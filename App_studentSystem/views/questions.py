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
    quesList = sorted(list(quesList_raw),
                      key=lambda x: x.seconded-x.disliked, reverse=True)
    msg["quesNum"] = len(quesList)
    msg["questions"] = quesList2dict(quesList)
    outputMsg(msg)
    return render(request, "student/display_all.html", msg)


def display_mine(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList = list(getmyquestions(hash).filter(week=week))
    msg["quesNum"] = len(quesList)
    msg["questions"] = quesList2dict(quesList)
    outputMsg(msg)
    return render(request, "student/display_mine.html", msg)


