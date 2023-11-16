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
    pagenum = request.COOKIES.get("pgnm")
    pagenum = int(pagenum) + 1 if pagenum else 1
    if request.POST:
        _Setting = request.POST.getlist("Setting")
        if "R" in _Setting or request.COOKIES.get("Setting_R")=="R":
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
            q["evaluation"] = get_evaluation(i.pk)
            q["cnt"] = cnt
            questions[i.pk] = q

    msg["questions"] = questions
    msg["realquesnum"] = len(quesList)
    msg["page"] = pagenum
    msg["totalpagenum"] = totalpagenum

    outputMsg(msg)
    ret = render(request, "admin/respond.html", msg)
    ret.delete_cookie("responded")
    ret.delete_cookie("pgnm")
    ret.delete_cookie("Setting_R")

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
            if i[:2] == "_Q":
                eva_ques(int(i[2:]), j)
        ret.set_cookie("pgnm",request.POST["pgnm"])
        ret.set_cookie("Setting_R","R" if request.POST.get("Setting") else "N")
    return ret


def rsp_ques(quesID: int, hash: str, rsp: str, week:int):
    originResponse = get_response(quesID, hash)
    if originResponse == rsp:
        return
    else:
        set_response(quesID, hash, rsp, week)


def eva_ques(quesID: int, eva: str):
    q = quesBaseInfo.objects.get(pk=quesID)
    if eva == "S":
        q.adminseconded = True
        q.admindisliked = False
    if eva == "N":
        q.adminseconded = False
        q.admindisliked = False
    if eva == "D":
        q.adminseconded = False
        q.admindisliked = True
    q.save()