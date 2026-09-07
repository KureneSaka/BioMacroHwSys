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
    """Return the pk of the week that is currently in progress.

    - no week rows           -> 0 (callers must tolerate it via initweekdict)
    - earliest week not begun -> the earliest week (course not started yet)
    - otherwise               -> the latest week whose timeBegin has passed
    """
    now = datetime.datetime.now()
    weeklist = list(weekDB.objects.all().order_by("timeBegin"))
    if not weeklist:
        return 0
    current = None
    for w in weeklist:
        if w.timeBegin <= now:
            current = w
        else:
            break
    if current is None:
        current = weeklist[0]
    return current.pk


def checkweek(request: HttpRequest):
    wk = request.COOKIES.get("week")
    if wk:
        wk = int(wk)
    else:
        wk = initialweek()
    return initweekdict(wk), wk


def initweekdict(wk: int) -> dict:
    ret = {"weeknum": None, "lecture": None}
    try:
        w = weekDB.objects.get(pk=wk)
    except weekDB.DoesNotExist:
        return ret
    ret["weeknum"] = w.week
    lec_bgn = w.lectureBegin
    lec_fin = w.lectureFinish
    if lec_bgn == lec_fin:
        ret["lecture"] = f"Lec.{lec_bgn}"
    else:
        ret["lecture"] = f"Lec.{lec_bgn}~{lec_fin}"
    return ret


def check_submit_open(week: int):
    """Return None if questions may be submitted this week, else a reason str."""
    try:
        w = weekDB.objects.get(pk=week)
    except weekDB.DoesNotExist:
        return None
    now = datetime.datetime.now()
    if now < w.timeBegin:
        return "本周活动尚未开始，暂不能提交"
    if now > w.timeSubmitFinish:
        return "本次提交已截止"
    return None


def check_evaluate_open(week: int):
    """Return None if evaluating/responding is allowed this week, else reason."""
    try:
        w = weekDB.objects.get(pk=week)
    except weekDB.DoesNotExist:
        return None
    now = datetime.datetime.now()
    if now < w.timeBegin:
        return "本周活动尚未开始"
    if now > w.timeEvaluateFinish:
        return "本次评价与互答已截止"
    return None
