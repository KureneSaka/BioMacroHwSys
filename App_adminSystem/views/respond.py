# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *

def respond(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getallquestions().filter(week=week,visible=True)
    originQuesList = sorted(list(quesList_raw),
                      key=lambda x: x.seconded-x.disliked, reverse=True)
    msg["quesNum"] = quesList_raw.count()

    quesList = originQuesList.copy()
    pagenum = 1
    if request.POST:
        _Setting = request.POST.getlist("Setting")
        if "R" in _Setting:
            msg["Setting_R"] = True
            for i in originQuesList:
                if get_response(i.pk, hash):
                    quesList.remove(i)
        page_setting = request.POST.getlist("page_setting")
        if page_setting:
            try:
                pagenum = int(request.POST["pagenum"])
            except:
                pagenum = int(request.POST["pgnm"])
            if "S" in page_setting:
                pagenum = pagenum
            if "P" in page_setting:
                pagenum = pagenum - 1
            if "N" in page_setting:
                pagenum = pagenum + 1
        else:
            pagenum = 1
    totalpagenum = int((len(quesList)+9)/10)
    if pagenum <= 0:
        pagenum = 1
    if pagenum > totalpagenum:
        pagenum = totalpagenum

    questions = {}
    cnt = 0
    for i in quesList:
        cnt = cnt+1
        if cnt > pagenum*10-10 and cnt <= pagenum*10:
            q = {}
            q["asker"] = stuid2name(i.studentID)
            q["seconded"] = i.seconded
            q["disliked"] = i.disliked
            q["question"] = i.question
            q["response"] = get_response(i.pk,hash)
            q["cnt"] = cnt
            questions[i.pk] = q

    msg["questions"] = questions
    msg["realquesnum"] = len(quesList)
    msg["page"] = pagenum
    msg["totalpagenum"] = totalpagenum

    outputMsg(msg)
    ret = render(request, "admin/respond.html", msg)
    ret.delete_cookie("responded")
    return ret


def responding(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    ret = redirect("/admin/respond")
    if request.POST:
        ret.set_cookie("responded", True)
        outputPost(request)
        for i, j in request.POST.items():
            if i[:2] == "_A":
                rsp_ques(int(i[2:]), hash, j.strip(), week)
    return ret


def rsp_ques(quesID: int, hash: str, rsp: str, week:int):
    originResponse = get_response(quesID, hash)
    if originResponse == rsp:
        return
    else:
        set_response(quesID, hash, rsp, week)
