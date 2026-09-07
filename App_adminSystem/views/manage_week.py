# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *
import datetime


def manage_week(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    msg = weekInfoDict()
    wkmsg, _ = checkweek(request)
    msg.update(wkmsg)
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    msg["gen_suc"] = request.session.pop("gen_suc", None)
    msg["gen_err"] = request.session.pop("gen_err", None)
    ret = render(request, "admin/manage_week.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    return ret


def generate_weeks(request: HttpRequest):
    """One-click generate a whole semester's weekly schedule.

    The semester is split into 7-day windows starting from semester_begin.
    The three time inputs are the anchors of week 1; every later week is the
    same moment shifted by 7 days. lecture = week number (editable afterwards).
    """
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_week")
    try:
        begin = datetime.date.fromisoformat(request.POST["semester_begin"])
        end = datetime.date.fromisoformat(request.POST["semester_end"])
        t_begin = datetime.datetime.fromisoformat(request.POST["week_time_begin"])
        t_submit = datetime.datetime.fromisoformat(request.POST["week_time_submit"])
        t_evaluate = datetime.datetime.fromisoformat(request.POST["week_time_evaluate"])
    except (KeyError, ValueError):
        request.session["gen_err"] = "请完整填写学期起止日期与三个时间点（格式需正确）"
        return ret
    if end < begin:
        request.session["gen_err"] = "学期最后一天不能早于第一天"
        return ret
    if not (t_begin <= t_submit <= t_evaluate):
        request.session["gen_err"] = "时间需满足：每周开启 ≤ 本周提交截止 ≤ 本周评论结束"
        return ret
    week_end = begin + datetime.timedelta(days=6)
    if not (begin <= t_begin.date() <= week_end
            and begin <= t_submit.date() <= week_end):
        request.session["gen_err"] = (
            "开启时间与提交截止需落在第一周（%s ~ %s）内" % (begin, week_end))
        return ret

    days_total = (end - begin).days
    num = (days_total + 7) // 7
    conflicts = [k for k in range(1, num + 1)
                 if weekDB.objects.filter(week=k).exists()]
    if conflicts:
        request.session["gen_err"] = (
            "已存在周次 %s，为避免覆盖，本次未生成任何周次；可先删除这些周次后再生成"
            % "、".join(str(x) for x in conflicts))
        return ret

    from django.db import transaction
    rows = []
    for k in range(1, num + 1):
        offset = datetime.timedelta(days=(k - 1) * 7)
        rows.append(weekDB(week=k, lectureBegin=k, lectureFinish=k,
                           timeBegin=t_begin + offset,
                           timeSubmitFinish=t_submit + offset,
                           timeEvaluateFinish=t_evaluate + offset))
    with transaction.atomic():
        weekDB.objects.bulk_create(rows)
    last = rows[-1]
    request.session["gen_suc"] = (
        "已创建 %d 周：第 1 周 %s 开启，至第 %d 周（%s 评论结束）"
        % (num, t_begin.strftime("%Y-%m-%d"), num,
           last.timeEvaluateFinish.strftime("%Y-%m-%d")))
    ret = redirect("/admin/manage_week#weeklist")
    ret.set_cookie("week", initialweek())  # jump to the current (initial) week
    return ret


def add_week(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_week")
    if not (request.POST.get("week") and request.POST.get("lectureBegin")
            and request.POST.get("lectureFinish") and request.POST.get("timeBegin")
            and request.POST.get("timeSubmitFinish")
            and request.POST.get("timeEvaluateFinish")):
        ret.set_cookie("operate_err", "ME_W_A1")
        return ret
    try:
        week = int(request.POST["week"])
        lec_bgn = int(request.POST["lectureBegin"])
        lec_fin = int(request.POST["lectureFinish"])
        time_bgn = datetime.datetime.fromisoformat(request.POST["timeBegin"])
        time_sub = datetime.datetime.fromisoformat(request.POST["timeSubmitFinish"])
        time_eva = datetime.datetime.fromisoformat(request.POST["timeEvaluateFinish"])
    except (TypeError, ValueError):
        ret.set_cookie("operate_err", "ME_W_A2")
        return ret
    if week <= 0 or lec_bgn <= 0 or lec_fin < lec_bgn:
        ret.set_cookie("operate_err", "ME_W_A2")
        return ret
    if not (time_bgn <= time_sub <= time_eva):
        ret.set_cookie("operate_err", "ME_W_A4")
        return ret
    if weekDB.objects.filter(week=week).exists():
        ret.set_cookie("operate_err", "ME_W_A3")
        return ret
    w = weekDB(week=week, lectureBegin=lec_bgn, lectureFinish=lec_fin,
               timeBegin=time_bgn, timeSubmitFinish=time_sub,
               timeEvaluateFinish=time_eva)
    w.save()
    ret.set_cookie("operate_suc", "add")
    ret.set_cookie("week", initialweek())  # jump to the current (initial) week
    return ret


def modify_week(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_week")
    modify_selection = request.POST.get("modify_selection")
    if modify_selection == "Modify":
        e = modify_week_M(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "modify")
    elif modify_selection == "Delete":
        e = modify_week_D(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "delete")
            ret.set_cookie("week", initialweek())  # reset to current week after delete
    return ret


def modify_week_M(request: HttpRequest) -> str:
    for i, j in request.POST.lists():
        if i[:2] != "_M":
            continue
        if len(j) < 6 or any(not k for k in j):
            return "ME_W_M1"
        try:
            w = weekDB.objects.get(pk=int(i[2:]))
            new_week = int(j[0])
            lec_bgn = int(j[1])
            lec_fin = int(j[2])
            time_bgn = datetime.datetime.fromisoformat(j[3])
            time_sub = datetime.datetime.fromisoformat(j[4])
            time_eva = datetime.datetime.fromisoformat(j[5])
        except (TypeError, ValueError, weekDB.DoesNotExist):
            return "ME_W_M2"
        if new_week <= 0 or lec_bgn <= 0 or lec_fin < lec_bgn:
            return "ME_W_M2"
        if w.week != new_week and weekDB.objects.filter(week=new_week).exists():
            return "ME_W_M3"
        if not (time_bgn <= time_sub <= time_eva):
            return "ME_W_M4"
        w.week = new_week
        w.lectureBegin = lec_bgn
        w.lectureFinish = lec_fin
        w.timeBegin = time_bgn
        w.timeSubmitFinish = time_sub
        w.timeEvaluateFinish = time_eva
        w.save()
    return None


def modify_week_D(request: HttpRequest) -> str:
    to_delete = request.POST.getlist("to_delete")
    if not to_delete:
        return "ME_W_D1"
    for i in to_delete:
        try:
            pk_i = int(i)
        except (TypeError, ValueError):
            return "ME_W_D1"
        if quesBaseInfo.objects.filter(week=pk_i).exists():
            return "ME_W_D2"
        weekDB.objects.filter(pk=pk_i).delete()
    return None


def weekInfoDict() -> dict:
    ret = {}
    weekList = weekDB.objects.all().order_by("week")
    ret["weekNum"] = weekList.count()
    weeks = {}
    for i in weekList:
        w = {}
        w["week"] = i.week
        w["lectureBegin"] = i.lectureBegin
        w["lectureFinish"] = i.lectureFinish
        w["timeBegin"] = i.timeBegin
        w["timeSubmitFinish"] = i.timeSubmitFinish
        w["timeEvaluateFinish"] = i.timeEvaluateFinish
        w["quesNum"] = quesBaseInfo.objects.filter(week=i.pk).count()
        weeks[i.pk] = w
    ret["weeks"] = weeks
    return ret


def check_manage_error(err: str):
    e: str
    if err == None:
        e = None
    elif err == "ME_W_A1":
        e = "周次信息不完整，请重新输入"
    elif err == "ME_W_A2":
        e = "周次或章节格式有误，请重新输入"
    elif err == "ME_W_A3":
        e = "周次重复，请重新输入"
    elif err == "ME_W_A4":
        e = "时间格式或先后顺序有误，请重新输入"
    elif err == "ME_W_M1":
        e = "周次信息不完整，请重新修改"
    elif err == "ME_W_M2":
        e = "周次或章节格式有误，请重新修改"
    elif err == "ME_W_M3":
        e = "周次重复，请重新修改"
    elif err == "ME_W_M4":
        e = "时间格式或先后顺序有误，请重新修改"
    elif err == "ME_W_D1":
        e = "您未选中任何周次"
    elif err == "ME_W_D2":
        e = "所选周次下已有问题，无法删除"
    else:
        e = "意外错误"
    return e
