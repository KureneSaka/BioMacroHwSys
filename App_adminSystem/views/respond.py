# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *

def respond(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg = {}
    quesList_raw = getallquestions()
    quesList = sorted(list(quesList_raw),
                      key=lambda x: x.seconded-x.disliked, reverse=True)
    msg["quesNum"] = quesList_raw.count()
    outputPost(request)
    quesList = quesList.copy()
    _Setting = request.POST.getlist("Setting")
    if "T" in _Setting:
        msg["Setting_T"] = True
        for i in quesList:
            if get_response(i.pk, hash):
                quesList.remove(i)

    realnum = min(msg["quesNum"], len(quesList))

    questions = {}
    cnt = 0
    for i in quesList:
        q = {}
        q["asker"] = stuid2name(i.studentID)
        q["seconded"] = i.seconded
        q["disliked"] = i.disliked
        q["question"] = i.question
        q["response"] = get_response(i.pk,hash)
        cnt = cnt+1
        q["cnt"] = cnt
        questions[i.pk] = q

    msg["questions"] = questions
    msg["realquesnum"] = realnum

    outputMsg(msg)
    ret = render(request, "admin/respond.html", msg)
    return ret


def responding(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/admin/respond")
    if request.POST:
        outputPost(request)
        for i, j in request.POST.items():
            if i[:2] == "_A":
                rsp_ques(int(i[2:]), hash, j)
    return ret


def rsp_ques(quesID: int, hash: str, rsp: str):
    originResponse = get_response(quesID, hash)
    if originResponse == rsp:
        return
    else:
        set_response(quesID, hash, rsp)
