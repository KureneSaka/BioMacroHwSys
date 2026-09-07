# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from App_dataSystem.models import UserProfile
from .utils import *
import secrets


def manage_admin(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    msg = adminInfoDict(request.user.pk)
    wkmsg, _ = checkweek(request)
    msg.update(wkmsg)
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    msg["pwd"] = request.COOKIES.get("operate_pwd")
    ret = render(request, "admin/manage_admin.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    ret.delete_cookie("operate_pwd")
    return ret


def _new_random_pwd() -> str:
    return secrets.token_hex(4)


def add_admin(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_admin")
    username = (request.POST.get("username") or "").strip()
    name = (request.POST.get("name") or "").strip()
    if not username or not name:
        ret.set_cookie("operate_err", "ME_A_A1")
        return ret
    if User.objects.filter(username=username).exists():
        ret.set_cookie("operate_err", "ME_A_A3")
        return ret
    pwd = _new_random_pwd()
    u = User.objects.create_user(username=username, password=pwd,
                                 first_name=name, is_staff=True)
    UserProfile.objects.create(user=u, must_change_password=True)
    ret.set_cookie("operate_suc", "add")
    ret.set_cookie("operate_pwd", pwd)
    return ret


def modify_admin(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_admin")
    if request.POST.get("to_reset"):
        e, pwd = reset_admin_pwd(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "reset")
            ret.set_cookie("operate_pwd", pwd)
    elif request.POST.get("modify_selection") == "Modify":
        e = modify_admin_M(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "modify")
    elif request.POST.get("modify_selection") == "Delete":
        e = modify_admin_D(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "delete")
    return ret


def modify_admin_M(request: HttpRequest) -> str:
    for i, j in request.POST.lists():
        if i[:2] == "_M":
            name = j[0].strip() if j else ""
            if not name:
                return "ME_A_M1"
            u = User.objects.filter(pk=int(i[2:]), is_staff=True).first()
            if not u:
                return "ME_A_M2"
            u.first_name = name
            u.save()
    return None


def modify_admin_D(request: HttpRequest) -> str:
    to_delete = request.POST.getlist("to_delete")
    if not to_delete:
        return "ME_A_D1"
    for pk_i in to_delete:
        User.objects.filter(pk=int(pk_i), is_staff=True).delete()
    return None


def reset_admin_pwd(request: HttpRequest):
    pk_i = request.POST.get("to_reset")
    if not pk_i:
        return "ME_A_P1", None
    u = User.objects.filter(pk=int(pk_i), is_staff=True).first()
    if not u:
        return "ME_A_M2", None
    pwd = _new_random_pwd()
    u.set_password(pwd)
    u.save()
    profile, _ = UserProfile.objects.get_or_create(user=u)
    profile.must_change_password = True
    profile.save()
    return None, pwd


def adminInfoDict(pk: int) -> dict:
    ret = {}
    users = User.objects.filter(is_staff=True).exclude(pk=pk).order_by("username")
    ret["adminNum"] = users.count() + 1
    admins = {}
    for u in users:
        admins[u.pk] = {"username": u.username, "name": u.first_name}
    ret["admins"] = admins
    return ret


def check_manage_error(err: str):
    e: str
    if err == None:
        e = None
    elif err == "ME_A_A1":
        e = "用户名或姓名不能为空"
    elif err == "ME_A_A3":
        e = "用户名已存在"
    elif err == "ME_A_M1":
        e = "姓名不能为空"
    elif err == "ME_A_M2":
        e = "该管理员账号不存在"
    elif err == "ME_A_D1":
        e = "您未选中任何管理员"
    elif err == "ME_A_P1":
        e = "您未选中任何管理员"
    else:
        e = "意外错误"
    return e
