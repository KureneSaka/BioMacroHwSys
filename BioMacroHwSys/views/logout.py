# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout


def logout(request: HttpRequest):
    auth_logout(request)
    ret = redirect("/")
    ret.delete_cookie("week")
    return ret
