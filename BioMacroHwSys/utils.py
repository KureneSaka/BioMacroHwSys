from django.http import HttpRequest, HttpResponse, QueryDict
import time
from App_dataSystem.models import *
import datetime


def outputPost(request: HttpRequest):
    print("------[" + time.strftime('%d/%h/%Y %H:%M:%S') +
          "] Got a post from \"" + request.path + "\", POST is: ")
    print(request.POST)


def outputMsg(msg: dict):
    print("------[" + time.strftime('%d/%h/%Y %H:%M:%S') +
          "] Ready to send a response with msg: ")
    print(msg)


def initialweek() -> int:
    weeklist = weekDB.objects.all()
    for i in weeklist:
        if i.timeBegin < datetime.datetime.now():
            return i.pk
    return 0


def checkweek(request: HttpRequest):
    wk = request.COOKIES.get("week")
    if wk:
        wk = int(wk)
    else:
        wk = initialweek()
    return initweekdict(wk), wk


def initweekdict(wk: int) -> dict:
    w = weekDB.objects.get(pk=wk)
    ret = {}
    ret["weeknum"] = w.week
    lec_bgn = w.lectureBegin
    lec_fin = w.lectureFinish
    if lec_bgn == lec_fin:
        ret["lecture"] = f"Lec.{lec_bgn}"
    else:
        ret["lecture"] = f"Lec.{lec_bgn}~{lec_fin}"
    return ret
