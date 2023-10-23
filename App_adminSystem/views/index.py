# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def index(request:HttpRequest):
    hash,r = checkcookies(request)
    if r:
        return r
    msg, week = checkweek(request)
    msg["AdminName"] = hash2name(hash)
    return render(request, "admin/index.html", msg)
