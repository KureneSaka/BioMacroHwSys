from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from App_dataSystem.models import *
from BioMacroHwSys.utils import *
import datetime

def checkcookies(request: HttpRequest) -> (str, HttpResponse):
    loginCookies = request.COOKIES.get("is_login")
    if loginCookies and loginCookies[0] == 'A':
        return loginCookies[1:], None
    else:
        return None, redirect("/")


def checkhash(hash: str) -> (bool, str):
    try:
        s: adminBaseInfo
        try:
            s = adminBaseInfo.objects.get(hash=hash)
            return True, None
        except:
            raise Exception("E3")
    except Exception as e:
        err = str(e)
        if not(err == "E3"):
            err = "E9"
        return False, err


def checkerror(err: str) -> str:
    e: str
    if err == None:
        e = None
    elif err == "E3":
        e = "校验码错误"
    else:
        e = "意外错误，情报告管理员"
    return e


def stuid2name(id:int)->str:
    return stuBaseInfo.objects.get(studentID=id).name


def hash2name(hash: str) -> str:
    return adminBaseInfo.objects.get(hash=hash).name


def hash2pk(hash: str) -> int:
    return adminBaseInfo.objects.get(hash=hash).pk


def pk2name(pk:int)->str:
    return adminBaseInfo.objects.get(pk=pk).name


def getallquestions():
    return quesBaseInfo.objects.all()


def getstuquestions(id: int):
    return quesBaseInfo.objects.filter(studentID=id)


def getallresponses(pk: int):
    return quesResponseDB.objects.filter(quesID=pk, responded=True)


def get_evaluation(quesID: int) -> str:
    q = quesBaseInfo.objects.get(pk = quesID)
    if q.admindisliked:
        return "D"
    elif q.adminseconded:
        return "S"
    else:
        return "N"


def get_response(quesID: int, hash: str) -> str:
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="A", responderID=hash2pk(hash))
        return s.response if s.responded else ""
    except:
        return ""


def set_response(quesID: int, hash: str, rsp: str, week: int):
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="A", responderID=hash2pk(hash), week=week)
    except:
        s = quesResponseDB(quesID=quesID, responderType="A",
                           responderID=hash2pk(hash),week=week)
    s.responded = False if rsp == "" else True
    s.response = rsp
    s.save()


def quesList2dict(quesList: list[quesBaseInfo]) -> dict:
    '''
    question
    |-asker\n
    |-seconded\n
    |-disliked\n
    |-question\n
    |-date\n
    |-time\n
    |-cnt\n
    |-rowNum\n
    |-visible\n
    |-admindisliked\n
    |-adminseconded\n
    |-responses\n
    | |-adminrespond\n
    | |-responder\n
    | |-response\n
    | |-date\n
    | |-time\n
    '''
    questions = {}
    cnt = 0
    for i in quesList:
        q = {}
        try:
            q["asker"] = stuid2name(i.studentID)
        except:
            q["asker"] = "未知"
        q["seconded"] = i.seconded
        q["disliked"] = i.disliked
        q["question"] = i.question
        q["date"] = i.submitTime.strftime("%y/%m/%d")
        q["time"] = i.submitTime.strftime("%H:%M")
        q["visible"] = i.visible
        q["adminseconded"] = i.adminseconded
        q["admindisliked"] = i.admindisliked
        respList = getallresponses(i.pk)
        responses = {}
        for j in respList:
            r = {}
            r["adminrespond"] = True if j.responderType == "A" else False
            try:
                r["responder"] = pk2name(
                    j.responderID)if r["adminrespond"] else stuid2name(j.responderID)
            except:
                r["responder"] = "未知"
            r["response"] = j.response
            r["date"] = j.respondTime.strftime("%y/%m/%d")
            r["time"] = j.respondTime.strftime("%H:%M")
            responses[j.pk] = r
        q["rowNum"] = len(responses)+1
        q["responses"] = responses
        cnt = cnt+1
        q["cnt"] = cnt
        questions[i.pk] = q
    return questions
