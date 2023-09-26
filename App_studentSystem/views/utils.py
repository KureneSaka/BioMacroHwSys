from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from App_dataSystem.models import *

def checkcookies(request: HttpRequest) -> (str, HttpResponse):
    loginCookies = request.COOKIES.get("is_login")
    if loginCookies and loginCookies[0] == 'A':
        return loginCookies[1:], None
    else:
        return None, redirect("")


def checkhash(id: str, hash: str) -> (bool, Exception):
    try:
        try:
            int(id)
        except:
            raise Exception("学号输入错误")
        s: stuBaseInfo
        try:
            s = stuBaseInfo.objects.get(studentID=int(id))
        except:
            raise Exception("学号不在课程中")
        if s.hash==hash:
            return True, None
        else:
            raise Exception("校验码错误")
    except Exception as e:
        return False, e
