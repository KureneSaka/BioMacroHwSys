# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..utils import *
from ..auth import is_admin


def loginIndex(request: HttpRequest):
    ret = None
    if request.user.is_authenticated:
        if is_admin(request.user):
            ret = redirect("/admin/index")
        else:
            ret = redirect("/student/index")
    else:
        ret = render(request, "login.html")
    if not request.COOKIES.get("week"):
        ret.set_cookie("week", initialweek())
    return ret
