# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .utils import *


def manage_student(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    print(request.COOKIES)
    msg = stuInfoDict()
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    ret = render(request, "admin/manage_student.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    return ret


def add_student(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_student")
    try:
        if request.POST["name"] and request.POST["id"] and request.POST["hash"]:
            try:
                if int(request.POST["id"]) >= 10000000000:
                    raise Exception
            except:
                raise Exception("ME_S_A2")
            if stuBaseInfo.objects.filter(studentID=request.POST["id"]).count():
                raise Exception("ME_S_A3")
            if stuBaseInfo.objects.filter(hash=request.POST["hash"]).count():
                raise Exception("ME_S_A4")
        else:
            raise Exception("ME_S_A1")
    except Exception as e:
        ret.set_cookie("operate_err", e)
    else:
        s = stuBaseInfo(studentID=int(
            request.POST["id"]), name=request.POST["name"], hash=request.POST["hash"])
        s.save()
        ret.set_cookie("operate_suc", "add")
    return ret


def modify_student(request: HttpRequest):
    hash, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_student")
    modify_selection = request.POST.get("modify_selection")
    if modify_selection == "Modify":
        e = modify_student_M(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "modify")
    elif modify_selection == "Delete":
        e = modify_student_D(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "delete")
    return ret


def modify_student_M(request: HttpRequest) -> str:
    for i, j in request.POST.lists():
        if i[:2] == "_M":
            try:
                for k in j:
                    if not k:
                        raise Exception("ME_S_M1")
                try:
                    if int(j[0]) >= 10000000000:
                        raise Exception
                except:
                    raise Exception("ME_S_M2")
                s = stuBaseInfo.objects.get(pk=int(i[2:]))
                if s.studentID != int(j[0]):
                    if stuBaseInfo.objects.filter(studentID=int(j[0])).count():
                        raise Exception("ME_S_M3")
                if s.hash != j[2]:
                    if stuBaseInfo.objects.filter(hash=j[2]).count():
                        raise Exception("ME_S_M4")
                s.name = j[1]
                s.studentID = int(j[0])
                s.hash = j[2]
                s.save()
            except Exception as e:
                return e
    return None


def modify_student_D(request: HttpRequest) -> str:
    try:
        request.POST["to_delete"]
    except:
        return "ME_S_D1"
    else:
        for i in request.POST.getlist("to_delete"):
            s=stuBaseInfo.objects.get(pk=int(i))
            s.delete()
        return None


def stuInfoDict() -> dict:
    ret = {}
    stuList = stuBaseInfo.objects.all()
    ret["stuNum"] = stuList.count()
    students = {}
    for i in stuList:
        s = {}
        s["studentID"] = i.studentID
        s["name"] = i.name
        s["hash"] = i.hash
        students[i.pk] = s
    ret["students"] = students
    return ret


def check_manage_error(err: str):
    e: str
    if err == None:
        e = None
    elif err == "ME_S_A1":
        e = "学生信息不完整，请重新输入"
    elif err == "ME_S_A2":
        e = "学号必须为十位纯数字，请重新输入"
    elif err == "ME_S_A3":
        e = "学号重复，请重新输入"
    elif err == "ME_S_A4":
        e = "校验码重复，请重新输入"
    elif err == "ME_S_M1":
        e = "学生信息不完整，请重新修改"
    elif err == "ME_S_M2":
        e = "学号必须为十位纯数字，请重新修改"
    elif err == "ME_S_M3":
        e = "学号重复，请重新修改"
    elif err == "ME_S_M4":
        e = "校验码重复，请重新修改"
    elif err == "ME_S_D1":
        e = "您未选中任何学生"
    else:
        e = "意外错误"
    return e
