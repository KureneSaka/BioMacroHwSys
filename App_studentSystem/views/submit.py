# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *

def submit(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    if request.POST:
        outputPost(request)
        quesList=request.POST.getlist("quesList")
        for q in quesList:
            if q:
                savequestion(hash, q)
    originQuesNum = hash2quesnum(hash)
    msg = {}
    msg["StuQuesNum"] = originQuesNum
    labelList = []
    for i in range(1, 6):
        labelList.append(f"问题{i+originQuesNum}")
    msg["labelList"] = labelList
    return render(request, "student/submit.html", msg)


def savequestion(hash: str, ques: str):
    q = quesBaseInfo(question=ques, studentID=hash2id(hash))
    q.save()
