# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *
import random

def respond(request:HttpRequest):
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
        if "T" in randomSetting:
            msg["randomSetting_T"] = True
            for i in originQuesList:
                if get_response(i.pk, hash):
                    quesList.remove(i)

        realnum = min(randquesnum, len(quesList))
        quesList_rand = random.sample(quesList, realnum)
        for i in quesList_rand:
            q = {}
            q["question"] = i.question
            q["response"] = get_response(i.pk, hash)
            questions[i.pk] = q
        msg["questions"] = questions
        msg["realquesnum"] = realnum

    if request.COOKIES.get("responded"):
        msg["respond_suc"]=True

    outputMsg(msg)
    ret = render(request, "student/respond.html", msg)
    ret.delete_cookie("responded")
    return ret


def responding(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/student/respond")
    if request.POST:
        ret.set_cookie("responded",True)
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
