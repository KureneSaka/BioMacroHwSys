# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *
import random

def respond_evaluate(request:HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    quesList_raw = getallquestions().exclude(
        studentID=hash2id(hash)).filter(week=week)
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
            elif "R" in randomSetting:
                if get_response(i.pk, hash):
                    quesList.remove(i)

        realnum = min(randquesnum, len(quesList))
        quesList_rand = random.sample(quesList, realnum)
        for i in quesList_rand:
            q = {}
            q["question"] = i.question
            q["response"] = get_response(i.pk, hash)
            q["evaluation"] = get_evaluation(i.pk, hash)
            respList = getallresponses(i.pk).exclude(responderID=hash2id(hash))
            responses = {}
            for j in respList:
                r = {}
                r["adminrespond"] = True if j.responderType == "A" else False
                r["response"] = j.response
                responses[j.pk] = r
            q["rowNum"] = len(responses)+1
            q["responses"] = responses
            questions[i.pk] = q
        msg["questions"] = {k: v for k, v in sorted(
            questions.items(), key=lambda x: x[0])}
        msg["realquesnum"] = realnum

        for i in randomSetting:
            msg["randomSetting_"+i] = True

    if request.COOKIES.get("resp_eva_ed"):
        msg["resp_eva_suc"] = True

    outputMsg(msg)
    ret = render(request, "student/respond_evaluate.html", msg)
    ret.delete_cookie("resp_eva_ed")
    return ret


def respond_evaluate_ing(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    ret = redirect("/student/respond_evaluate")
    if request.POST:
        ret.set_cookie("resp_eva_ed", True)
        outputPost(request)
        for i, j in request.POST.items():
            if i[:2] == "_A":
                rsp_ques(int(i[2:]), hash, j.strip(), week)
            if i[:2] == "_Q":
                eva_ques(int(i[2:]), hash, j)
    return ret


def rsp_ques(quesID: int, hash: str, rsp: str, week: int):
    originResponse = get_response(quesID, hash)
    if originResponse == rsp:
        return
    else:
        set_response(quesID, hash, rsp, week)


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
            q.disliked = q.disliked+1
        q.save()
        set_evaluation(quesID, hash, eva)
