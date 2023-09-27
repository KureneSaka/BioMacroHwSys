# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *

def display_all(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg = {}
    '''
    queslist/-seconded
            |-disliked
            |-question
            |-responses/-responderType
            \          \-response
    '''
    quesList = getallquestions()
    questions={}
    for i in quesList:
        q = {}
        q["seconded"] = i.seconded
        q["disliked"] = i.disliked
        q["question"] = i.question
        q["date"] = i.submitTime.strftime("%y/%m/%d")
        q["time"] = i.submitTime.strftime("%H:%M")
        respList = getallresponses(i.pk)
        responses = {}
        for j in respList:
            r = {}
            r["adminrespond"] = True if j.responderType == "A" else False
            r["response"] = j.response
            r["date"] = j.respondTime.strftime("%y/%m/%d")
            r["time"] = j.respondTime.strftime("%H:%M")
            responses[j.pk] = r
        q["columnNum"]=respList.count()+1
        q["responses"] = responses
        questions[i.pk] = q
    msg["quesNum"] = quesList.count()
    msg["questions"] = {k: v for k, v in sorted(
        questions.items(), key=lambda x: x[1]['seconded'], reverse=True)}
    print(msg)
    return render(request, "student/display_all.html", msg)
