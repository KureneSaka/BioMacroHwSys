# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def manage_admin(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    msg = adminInfoDict(hash)
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    ret = render(request, "admin/manage_admin.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    return ret


def add_admin(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_admin")
    try:
        if request.POST["name"] and request.POST["hash"]:
            if adminBaseInfo.objects.filter(hash=request.POST["hash"]).count():
                raise Exception("ME_A_A4")
        else:
            raise Exception("ME_A_A1")
    except Exception as e:
        ret.set_cookie("operate_err", e)
    else:
        s = adminBaseInfo(name=request.POST["name"], hash=request.POST["hash"])
        s.save()
        ret.set_cookie("operate_suc", "add")
    return ret


def modify_admin(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_admin")
    modify_selection = request.POST.get("modify_selection")
    if modify_selection == "Modify":
        e = modify_admin_M(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "modify")
    elif modify_selection == "Delete":
        e = modify_admin_D(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "delete")
    return ret


def modify_admin_M(request: HttpRequest) -> str:
    for i, j in request.POST.lists():
        if i[:2] == "_M":
            try:
                for k in j:
                    if not k:
                        raise Exception("ME_A_M1")
                s = adminBaseInfo.objects.get(pk=int(i[2:]))
                if s.hash != j[2]:
                    if adminBaseInfo.objects.filter(hash=j[2]).count():
                        raise Exception("ME_A_M4")
                s.name = j[0]
                s.hash = j[1]
                s.save()
            except Exception as e:
                return e
    return None


def modify_admin_D(request: HttpRequest) -> str:
    try:
        request.POST["to_delete"]
    except:
        return "ME_A_D1"
    else:
        for i in request.POST.getlist("to_delete"):
            s = adminBaseInfo.objects.get(pk=int(i))
            s.delete()
        return None


def adminInfoDict(hash:str) -> dict:
    ret = {}
    adminList = adminBaseInfo.objects.all().exclude(hash=hash)
    ret["adminNum"] = adminList.count()+1
    admins = {}
    for i in adminList:
        s = {}
        s["name"] = i.name
        s["hash"] = i.hash
        admins[i.pk] = s
    ret["admins"] = admins
    return ret




def check_manage_error(err: str):
    e: str
    if err == None:
        e = None
    elif err == "ME_A_A1":
        e = "管理员信息不完整，请重新输入"
    elif err == "ME_A_A4":
        e = "校验码重复，请重新输入"
    elif err == "ME_A_M1":
        e = "管理员信息不完整，请重新修改"
    elif err == "ME_A_M4":
        e = "校验码重复，请重新修改"
    elif err == "ME_A_D1":
        e = "您未选中任何管理员"
    else:
        e = "意外错误"
    return e
