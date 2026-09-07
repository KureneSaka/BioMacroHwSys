# -*- coding: utf-8 -*-
"""Shared change-password page for both students and admins.

Reachable at /student/change_pwd and /admin/change_pwd. Must_change_password
users are redirected here by checkcookies until they set a new password.
"""
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from App_dataSystem.models import UserProfile
from ..auth import must_change_password


def change_pwd(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("/")
    is_admin = request.user.is_staff
    base = "admin/base.html" if is_admin else "student/base.html"
    home = "/admin/index" if is_admin else "/student/index"
    msg = {"base_template": base, "must": must_change_password(request.user)}
    if request.POST:
        old = request.POST.get("old_password") or ""
        new1 = request.POST.get("new_password1") or ""
        new2 = request.POST.get("new_password2") or ""
        if not request.user.check_password(old):
            msg["err"] = "原密码错误"
        elif not new1:
            msg["err"] = "新密码不能为空"
        elif new1 != new2:
            msg["err"] = "两次输入的新密码不一致"
        else:
            try:
                validate_password(new1, user=request.user)
            except ValidationError as e:
                msg["err"] = "；".join(e.messages)
            else:
                request.user.set_password(new1)
                request.user.save()
                UserProfile.objects.filter(
                    user=request.user).update(must_change_password=False)
                update_session_auth_hash(request, request.user)
                return redirect(home)
    return render(request, "change_pwd.html", msg)
