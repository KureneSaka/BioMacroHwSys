# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from .utils import *

def next_week(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    wk = request.COOKIES.get("week")
    if wk:
        wk = int(wk)
    else:
        wk = initialweek()
    wk = wk + 1
    try:
        weekDB.objects.get(pk=wk)
    except:
        wk = wk - 1
    ret = redirect("/admin/index")
    ret.set_cookie("week", wk)
    return ret

def prev_week(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    wk = request.COOKIES.get("week")
    if wk:
        wk = int(wk)
    else:
        wk = initialweek()
    wk = wk - 1
    try:
        weekDB.objects.get(pk=wk)
    except:
        wk = wk + 1
    ret = redirect("/admin/index")
    ret.set_cookie("week", wk)
    return ret



def change_week(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    ret = redirect("/admin/index")
    if request.POST:
        try:
            wk = int(request.POST["weeknum"])
            w = weekDB.objects.get(week=wk)
            ret.set_cookie("week", w.pk)
            return ret
        except:
            return ret