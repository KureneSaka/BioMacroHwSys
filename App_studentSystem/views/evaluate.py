# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *
import random

def evaluate(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg = {}
    quesList_raw = getallquestions().exclude(studentID=hash2id(hash))
    msg["quesNum"] = quesList_raw.count()
    if request.POST:
        outputPost(request)
        try:
            randquesnum = int(request.POST["randquesnum"])
            msg["randquesnum"] = randquesnum
        except:
            randquesnum = 0
        questions = {}
        originQuesList=list(quesList_raw)
        quesList = list(quesList_raw)
        randomSetting = request.POST.getlist("randomSetting")

        for i in originQuesList:
            if get_evaluation(i.pk, hash) in randomSetting:
                quesList.remove(i)

        realnum = min(randquesnum, len(quesList))
        quesList_rand = random.sample(quesList, realnum)
        for i in quesList_rand:
            q = {}
            q["question"] = i.question
            q["evaluation"] = get_evaluation(i.pk, hash)
            questions[i.pk] = q
        msg["questions"] = questions
        msg["realquesnum"] = realnum
        for i in randomSetting:
            msg["randomSetting_"+i] = True

    if request.COOKIES.get("seconded"):
        msg["second_suc"]=True

    outputMsg(msg)
    ret = render(request, "student/second.html", msg)
    ret.delete_cookie("seconded")
    return ret


def evaluating(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/student/second")
    if request.POST:
        ret.set_cookie("seconded",True)
        outputPost(request)
        for i, j in request.POST.items():
            if i[:2] == "_Q":
                eva_ques(int(i[2:]), hash, j)
    return ret


def eva_ques(quesID: int, hash: str, eva: str):
    originEvaluate = get_evaluation(quesID, hash)
    if originEvaluate is eva:
        return
    else:
        q = quesBaseInfo.objects.get(pk=quesID)
        if originEvaluate == "S":
            q.seconded = q.seconded-1
        elif originEvaluate == "D":
            q.disliked = q.disliked-1
        if eva == "S":
            q.seconded = q.seconded+1
        elif eva == "D":
            q.disliked = q.disliked-1
        q.save()
        set_evaluation(quesID, hash, eva)
