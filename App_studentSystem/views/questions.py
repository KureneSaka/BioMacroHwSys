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
    sid, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList = list(getmyquestions(sid).filter(week=week))
    msg["quesNum"] = len(quesList)
    msg["questions"] = quesList2dict(quesList)

    if request.COOKIES.get("deleted"):
        msg["delete_suc"] = request.COOKIES.get("deleted")
    if request.COOKIES.get("undo_deleted"):
        msg["undo_delete_suc"] = request.COOKIES.get("undo_deleted")
    outputMsg(msg)
    ret = render(request, "student/display_mine.html", msg)
    ret.delete_cookie("deleted")
    ret.delete_cookie("undo_deleted")
    return ret


def deleting(request: HttpRequest):
    sid, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/student/display_mine")
    if request.POST:
        outputPost(request)
        to_delete = request.POST.get("to_delete")
        # only allow soft-deleting one's own question (fixes ownership bypass)
        if to_delete and del_ques(int(to_delete), sid):
            ret.set_cookie("deleted", to_delete)
    return ret


def del_ques(quespk: int, sid: int) -> bool:
    q = quesBaseInfo.objects.filter(pk=quespk, studentID=sid).first()
    if not q:
        return False
    q.visible = False
    q.save()
    return True


def undo_delete(request: HttpRequest):
    sid, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/student/display_mine")
    if request.POST:
        outputPost(request)
        undo_delete = request.POST.get("undo_delete")
        # only allow undoing deletion of one's own question
        if undo_delete and undel_ques(int(undo_delete), sid):
            ret.set_cookie("undo_deleted", undo_delete)
    return ret


def undel_ques(quespk: int, sid: int) -> bool:
    q = quesBaseInfo.objects.filter(pk=quespk, studentID=sid).first()
    if not q:
        return False
    q.visible = True
    q.save()
    return True
