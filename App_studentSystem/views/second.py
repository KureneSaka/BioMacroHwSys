# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *
import random

def second(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg = {}
    quesList_raw = getallquestions().exclude(studentID=hash2id(hash))
    msg["quesNum"] = quesList_raw.count()
    if request.POST:
        print(request.POST)
        try:
            randquesnum = int(request.POST["randquesnum"])
            msg["randquesnum"] = randquesnum
        except:
            randquesnum = 0
        questions = {}
        originQuesList=list(quesList_raw)
        quesList = list(quesList_raw)
        print(originQuesList)
        for i in originQuesList:
            if is_seconded(i.pk, hash) or is_disliked(i.pk, hash):
                quesList.remove(i)

        realnum = min(randquesnum, len(quesList))
        quesList_rand = random.sample(quesList, realnum)
        for i in quesList_rand:
            q = {}
            q["question"] = i.question
            questions[i.pk] = q
        msg["questions"] = questions
        msg["realquesnum"] = realnum

    if request.COOKIES.get("seconded"):
        msg["second_suc"]=True

    print(msg)
    ret = render(request, "student/second.html", msg)
    ret.delete_cookie("seconded")
    return ret


def seconding(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/student/second")
    if request.POST:
        ret.set_cookie("seconded",True)
        print(request.POST)
        for i in request.POST.getlist("to_second"):
            second_ques(int(i), hash)
        for i in request.POST.getlist("to_dislike"):
            dislike_ques(int(i), hash)
    return ret


def second_ques(quesID: int, hash: str):
    q = quesSecondDB(quesID=quesID, studentID=hash2id(hash))
    q.save()


def dislike_ques(quesID: int, hash: str):
    q = quesDislikeDB(quesID=quesID, studentID=hash2id(hash))
    q.save()
