# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def index(request:HttpRequest):
    hash,r = checkcookies(request)
    if r:
        return r
    msg = {}
    msg["StuName"] = hash2name(hash)
    msg["StuId"] = hash2id(hash)
    msg["StuQuesNum"] = hash2quesnum(hash)
    msg["StuRespNum"] = hash2respnum(hash)
    return render(request, "student/index.html", msg)
