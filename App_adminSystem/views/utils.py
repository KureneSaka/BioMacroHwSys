from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from App_dataSystem.models import *
from App_dataSystem.display import *
from BioMacroHwSys.utils import *
from BioMacroHwSys.auth import (CHANGE_PWD_PATHS, is_admin, must_change_password,
                                pwd_url)
import datetime

def checkcookies(request: HttpRequest) -> (int, HttpResponse):
    """Admin guard. Returns (admin User pk, None) or (None, redirect).

    Forces a password change before using the system when must_change_password
    is set (except on the change-pwd page).
    """
    if not is_admin(request.user):
        return None, redirect("/")
    if request.path not in CHANGE_PWD_PATHS and must_change_password(request.user):
        return None, redirect(pwd_url(request.user))
    return request.user.pk, None


def checkerror(err: str) -> str:
    e: str
    if err == None:
        e = None
    elif err == "E1":
        e = "请输入用户名"
    elif err == "E2":
        e = "账号不存在"
    elif err == "E3":
        e = "密码错误"
    elif err == "E4":
        e = "该账号不是管理员，请从学生入口登录"
    else:
        e = "意外错误，情报告管理员"
    return e


def getallquestions():
    return quesBaseInfo.objects.all()


def getstuquestions(id: int):
    return quesBaseInfo.objects.filter(studentID=id)


def get_evaluation(quesID: int) -> str:
    q = quesBaseInfo.objects.get(pk = quesID)
    if q.admindisliked:
        return "D"
    elif q.adminseconded:
        return "S"
    else:
        return "N"


def get_response(quesID: int, pk: int) -> str:
    """Admin's own response to a question (pk = admin User pk)."""
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="A", responderID=pk)
        return s.response if s.responded else ""
    except quesResponseDB.DoesNotExist:
        return ""


def set_response(quesID: int, pk: int, rsp: str, week: int):
    try:
        s = quesResponseDB.objects.get(
            quesID=quesID, responderType="A", responderID=pk, week=week)
    except quesResponseDB.DoesNotExist:
        s = quesResponseDB(quesID=quesID, responderType="A",
                           responderID=pk, week=week)
    s.responded = False if rsp == "" else True
    s.response = rsp
    s.save()

