from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from App_dataSystem.models import *
from BioMacroHwSys.utils import *
from BioMacroHwSys.auth import (CHANGE_PWD_PATHS, is_student, student_sid,
                                must_change_password, pwd_url)

def checkcookies(request: HttpRequest) -> (int, HttpResponse):
    """Student guard. Returns (student id, None) or (None, redirect).

    Also forces a password change before using the system when the
    must_change_password flag is set (except on the change-pwd page).
    """
    if not is_student(request.user):
        return None, redirect("/")
    if request.path not in CHANGE_PWD_PATHS and must_change_password(request.user):
        return None, redirect(pwd_url(request.user))
    return student_sid(request.user), None


def checkerror(err: str) -> str:
    e: str
    if err == None:
        e = None
    elif err == "E1":
        e = "学号格式有误"
    elif err == "E2":
        e = "账号不存在，请确认学号是否正确"
    elif err == "E3":
        e = "密码错误"
    elif err == "E4":
        e = "该账号为管理员，请从管理员入口登录"
    else:
        e = "意外错误，情报告管理员"
    return e


def name_of(sid: int) -> str:
    """Student full name by student id (User.first_name)."""
    try:
        return User.objects.get(username=str(sid)).first_name
    except User.DoesNotExist:
        return "未知"


def hash2quesnum(sid: int, week: int) -> int:
    return quesBaseInfo.objects.filter(studentID=sid, week=week, visible=True).count()


def hash2respnum(sid: int, week: int) -> int:
    return quesResponseDB.objects.filter(responderType="S", responderID=sid, responded=True, week=week).count()


def getallquestions():
    return quesBaseInfo.objects.filter(visible=True)


def getmyquestions(sid: int):
    return quesBaseInfo.objects.filter(studentID=sid, visible=True)


def getallresponses(pk: int):
    return quesResponseDB.objects.filter(quesID=pk, responded=True)


def get_evaluation(quesID: int, sid: int) -> str:
    try:
        s = quesEvaluateDB.objects.get(quesID=quesID, studentID=sid).evaluation
        return s
    except quesEvaluateDB.DoesNotExist:
        return "N"


def set_evaluation(quesID: int, sid: int, eva: str):
    try:
        s = quesEvaluateDB.objects.get(quesID=quesID, studentID=sid)
    except quesEvaluateDB.DoesNotExist:
        s = quesEvaluateDB(quesID=quesID, studentID=sid)
    s.evaluation = eva
    s.save()


def get_response(quesID: int, sid: int) -> str:
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="S", responderID=sid)
        return s.response if s.responded else ""
    except quesResponseDB.DoesNotExist:
        return ""


def set_response(quesID: int, sid: int, rsp: str, week: int):
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="S", responderID=sid, week=week)
    except quesResponseDB.DoesNotExist:
        s = quesResponseDB(quesID=quesID, responderType="S",
                           responderID=sid, week=week)
    s.responded = False if rsp == "" else True
    s.response = rsp
    s.save()

def quesList2dict(quesList: list[quesBaseInfo]) -> dict:
    '''
    question
    |-seconded\n
    |-disliked\n
    |-question\n
    |-date\n
    |-time\n
    |-cnt\n
    |-rowNum\n
    |-admindisliked\n
    |-adminseconded\n
    |-responses\n
    | |-adminrespond\n
    | |-response\n
    | |-date\n
    | |-time\n
    '''
    questions = {}
    cnt = 0
    for i in quesList:
        q = {}
        q["seconded"] = i.seconded
        q["disliked"] = i.disliked
        q["question"] = i.question
        q["date"] = i.submitTime.strftime("%y/%m/%d")
        q["time"] = i.submitTime.strftime("%H:%M")
        q["adminseconded"] = i.adminseconded
        q["admindisliked"] = i.admindisliked
        respList = getallresponses(i.pk)
        responses = {}
        for j in respList:
            r = {}
            r["adminrespond"] = True if j.responderType == "A" else False
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
