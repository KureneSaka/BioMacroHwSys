# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def index(request:HttpRequest):
    pk,r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    msg["AdminName"] = request.user.first_name
    return render(request, "admin/index.html", msg)
