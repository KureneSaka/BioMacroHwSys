# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect


def logout(request: HttpRequest):
    ret = redirect("/")
    ret.delete_cookie("is_login")
    return ret
