from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from App_dataSystem.models import *
from BioMacroHwSys.utils import *

def checkcookies(request: HttpRequest) -> (str, HttpResponse):
    loginCookies = request.COOKIES.get("is_login")
    if loginCookies and loginCookies[0] == 'S':
        return loginCookies[1:], None
    else:
        return None, redirect("/")


def checkhash(id: str, hash: str) -> (bool, str):
    try:
        try:
            int(id)
        except:
            raise Exception("E1")
        s: stuBaseInfo
        try:
            s = stuBaseInfo.objects.get(studentID=int(id))
        except:
            raise Exception("E2")
        if s.hash==hash:
            return True, None
        else:
            raise Exception("E3")
    except Exception as e:
        err=str(e)
        if not(err == "E1" or err == "E2" or err == "E3"):
            err = "E9"
        return False, err


def checkerror(err: str) -> str:
    e: str
    if err == "E1":
        e = "学号输入错误"
    elif err == "E2":
        e = "学号不在课程中"
    elif err == "E3":
        e = "校验码错误"
    elif err == None:
        e = None
    else:
        e = "意外错误，情报告管理员"
    return e


def hash2name(hash:str)->str:
    return stuBaseInfo.objects.get(hash = hash).name


def hash2id(hash: str) -> int:
    return stuBaseInfo.objects.get(hash=hash).studentID


def hash2pk(hash: str) -> int:
    return stuBaseInfo.objects.get(hash=hash).pk


def hash2quesnum(hash: str) -> int:
    return quesBaseInfo.objects.filter(studentID=hash2id(hash)).count()


def hash2respnum(hash: str) -> int:
    return quesResponseDB.objects.filter(responderType="S", responderID=hash2pk(hash)).count()


def getallquestions():
    return quesBaseInfo.objects.all()


def getmyquestions(hash: str):
    return quesBaseInfo.objects.filter(studentID=hash2id(hash))


def getallresponses(pk: int):
    return quesResponseDB.objects.filter(quesID=pk)


def get_evaluation(quesID: int, hash: str) -> str:
    try:
        s = quesEvaluateDB.objects.get(quesID=quesID, studentID=hash2id(hash)).evaluation
        return s
    except:
        return "N"


def set_evaluation(quesID: int, hash: str, eva: str):
    try:
        s = quesEvaluateDB.objects.get(quesID=quesID, studentID=hash2id(hash))
    except:
        s = quesEvaluateDB(quesID=quesID, studentID=hash2id(hash))
    s.evaluate = eva
    s.save()


def is_seconded(quesID: int, hash: str) -> bool:
    return True if get_evaluation(quesID,hash) == "S" else False

def is_disliked(quesID: int, hash: str) -> bool:
    return True if get_evaluation(quesID, hash) == "D" else False
