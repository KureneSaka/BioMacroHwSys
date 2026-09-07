# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import *

def submit(request:HttpRequest):
    sid, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    if request.POST:
        outputPost(request)
        closed = check_submit_open(week)
        if closed:
            messages.error(request, closed)
        else:
            quesList=request.POST.getlist("quesList")
            for q in quesList:
                if q:
                    savequestion(sid, q.strip(), week)
    originQuesNum = hash2quesnum(sid, week)
    msg["StuQuesNum"] = originQuesNum
    labelList = []
    for i in range(1, 6):
        labelList.append(f"问题{i+originQuesNum}")
    msg["labelList"] = labelList
    return render(request, "student/submit.html", msg)


def savequestion(sid: int, ques: str, week:int):
    q = quesBaseInfo(question=ques, studentID=sid, week=week)
    q.save()
