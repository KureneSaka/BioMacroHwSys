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
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    ret = redirect("/student/display_mine")
    if request.POST:
        ret.set_cookie("deleted", request.POST["to_delete"])
        outputPost(request)
        del_ques(int(request.POST["to_delete"]))
    return ret

def del_ques(quespk:int):
    q = quesBaseInfo.objects.get(pk=quespk)
    q.visible = False
    q.save()


def undo_delete(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    ret = redirect("/student/display_mine")
    if request.POST:
        ret.set_cookie("undo_deleted", request.POST["undo_delete"])
        outputPost(request)
        undel_ques(int(request.POST["undo_delete"]))
    return ret


def undel_ques(quespk: int):
    q = quesBaseInfo.objects.get(pk=quespk)
    q.visible = True
    q.save()
