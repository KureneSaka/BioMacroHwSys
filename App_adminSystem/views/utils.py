from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect


def checkcookies(request: HttpRequest) -> (str, HttpResponse):
    loginCookies = request.COOKIES.get("is_login")
    if loginCookies and loginCookies[0] == 'A':
        return loginCookies[1:], None
    else:
        return None, redirect("/")
