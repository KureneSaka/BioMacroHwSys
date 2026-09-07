# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .utils import *
import random

def evaluate(request:HttpRequest):
    sid, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getallquestions().exclude(studentID=sid).filter(week=week)
    msg["quesNum"] = quesList_raw.count()
    if request.POST:
        outputPost(request)
        try:
            randquesnum = int(request.POST["randquesnum"])
            msg["randquesnum"] = randquesnum
        except (KeyError, ValueError):
            randquesnum = 0
        questions = {}
        originQuesList=list(quesList_raw)
        quesList = list(quesList_raw)
        randomSetting = request.POST.getlist("randomSetting")

        for i in originQuesList:
            if get_evaluation(i.pk, sid) in randomSetting:
                quesList.remove(i)

        realnum = min(randquesnum, len(quesList))
        quesList_rand = random.sample(quesList, realnum)
        for i in quesList_rand:
            q = {}
            q["question"] = i.question
            q["evaluation"] = get_evaluation(i.pk, sid)
            questions[i.pk] = q
        msg["questions"] = questions
        msg["realquesnum"] = realnum
        for i in randomSetting:
            msg["randomSetting_"+i] = True

    if request.COOKIES.get("evaluated"):
        msg["evaluate_suc"]=True

    outputMsg(msg)
    ret = render(request, "student/evaluate.html", msg)
    ret.delete_cookie("evaluated")
    return ret


def evaluating(request:HttpRequest):
    sid, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    ret = redirect("/student/evaluate")
    if request.POST:
        outputPost(request)
        closed = check_evaluate_open(week)
        if closed:
            messages.error(request, closed)
            return ret
        ret.set_cookie("evaluated",True)
        for i, j in request.POST.items():
            if i[:2] == "_Q":
                eva_ques(int(i[2:]), sid, j)
    return ret


def eva_ques(quesID: int, sid: int, eva: str):
    with transaction.atomic():
        q = quesBaseInfo.objects.select_for_update().get(pk=quesID)
        old = get_evaluation(quesID, sid)
        if old == eva:
            return
        if old == "S":
            q.seconded = max(q.seconded - 1, 0)
        elif old == "D":
            q.disliked = max(q.disliked - 1, 0)
        if eva == "S":
            q.seconded += 1
        elif eva == "D":
            q.disliked += 1
        q.save()
        set_evaluation(quesID, sid, eva)
