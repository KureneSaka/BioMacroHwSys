# -*- coding: utf-8 -*-
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from App_dataSystem.models import UserProfile
from .utils import *
import secrets
import csv
import io
from datetime import datetime
from django.db import IntegrityError, transaction


def manage_student(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    msg = stuInfoDict()
    wkmsg, _ = checkweek(request)
    msg.update(wkmsg)
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    msg["pwd"] = request.COOKIES.get("operate_pwd")
    ret = render(request, "admin/manage_student.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    ret.delete_cookie("operate_pwd")
    return ret


def _new_random_pwd() -> str:
    return secrets.token_hex(4)


def add_student(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_student")
    sid = (request.POST.get("id") or "").strip()
    name = (request.POST.get("name") or "").strip()
    if not sid or not name:
        ret.set_cookie("operate_err", "ME_S_A1")
        return ret
    if not (sid.isdigit() and 4 < len(sid) <= 12):
        ret.set_cookie("operate_err", "ME_S_A2")
        return ret
    if User.objects.filter(username=sid).exists():
        ret.set_cookie("operate_err", "ME_S_A3")
        return ret
    pwd = _new_random_pwd()
    u = User.objects.create_user(username=sid, password=pwd, first_name=name)
    UserProfile.objects.create(user=u, must_change_password=True)
    ret.set_cookie("operate_suc", "add")
    ret.set_cookie("operate_pwd", pwd)
    return ret


def modify_student(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    outputPost(request)
    ret = redirect("/admin/manage_student")
    if request.POST.get("to_reset"):
        e, pwd = reset_student_pwd(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "reset")
            ret.set_cookie("operate_pwd", pwd)
    elif request.POST.get("modify_selection") == "Modify":
        e = modify_student_M(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "modify")
    elif request.POST.get("modify_selection") == "Delete":
        e = modify_student_D(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            ret.set_cookie("operate_suc", "delete")
    elif request.POST.get("modify_selection") == "ResetPwdExport":
        e, rows = reset_students_export(request)
        if e:
            ret.set_cookie("operate_err", e)
        else:
            # freshly generated passwords are returned only in this download
            return _pwd_csv_response(rows, prefix="reset_pwds")
    return ret


def modify_student_M(request: HttpRequest) -> str:
    for i, j in request.POST.lists():
        if i[:2] == "_M":
            name = j[0].strip() if j else ""
            if not name:
                return "ME_S_M1"
            u = User.objects.filter(pk=int(i[2:]), is_staff=False).first()
            if not u:
                return "ME_S_M2"
            u.first_name = name
            u.save()
    return None


def modify_student_D(request: HttpRequest) -> str:
    to_delete = request.POST.getlist("to_delete")
    if not to_delete:
        return "ME_S_D1"
    for pk_i in to_delete:
        User.objects.filter(pk=int(pk_i), is_staff=False).delete()
    return None


def reset_student_pwd(request: HttpRequest):
    pk_i = request.POST.get("to_reset")
    if not pk_i:
        return "ME_S_P1", None
    u = User.objects.filter(pk=int(pk_i), is_staff=False).first()
    if not u:
        return "ME_S_M2", None
    pwd = _new_random_pwd()
    u.set_password(pwd)
    u.save()
    profile, _ = UserProfile.objects.get_or_create(user=u)
    profile.must_change_password = True
    profile.save()
    return None, pwd


def reset_students_export(request: HttpRequest):
    """Reset selected students' passwords and return rows for CSV download.

    Plain passwords are never stored; they only exist inside the downloaded file.
    """
    selected = request.POST.getlist("to_delete")
    if not selected:
        return "ME_S_D1", []
    rows = []
    for pk_i in selected:
        u = User.objects.filter(pk=int(pk_i), is_staff=False).first()
        if not u:
            continue
        pwd = _new_random_pwd()
        u.set_password(pwd)
        u.save()
        profile, _ = UserProfile.objects.get_or_create(user=u)
        profile.must_change_password = True
        profile.save()
        rows.append({"username": u.username, "name": u.first_name, "password": pwd})
    if not rows:
        return "ME_S_D1", []
    return None, rows


def _find_col(headers: list, candidates) -> int:
    """Locate a header (case/space/underscore tolerant). Returns index or None."""
    norm = [h.strip().lower().replace(" ", "_") for h in headers]
    for cand in candidates:
        key = cand.strip().lower().replace(" ", "_")
        if key in norm:
            return norm.index(key)
    return None


def import_student_csv(request: HttpRequest):
    pk, r = checkcookies(request)
    if r:
        return r
    msg = stuInfoDict()
    wkmsg, _ = checkweek(request)
    msg.update(wkmsg)
    opsuc = request.COOKIES.get("operate_suc")
    if opsuc:
        msg[opsuc+"_suc"] = True
    msg["err"] = check_manage_error(request.COOKIES.get("operate_err"))
    if request.method == "POST" and request.FILES.get("csv"):
        raw = request.FILES["csv"].read()
        text = None
        for enc in ("utf-8-sig", "gbk"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            msg["import_err"] = "无法识别文件编码（支持 UTF-8 / GBK）"
        else:
            _run_import(msg, text, request)
    ret = render(request, "admin/manage_student.html", msg)
    ret.delete_cookie("operate_err")
    ret.delete_cookie("operate_suc")
    return ret


def _run_import(msg: dict, text: str, request) -> None:
    """Parse & import the CSV text into msg for the manage page to display.

    Strict mode: if ANY User Name already exists, nothing is imported and the
    offending student ids are reported instead.
    """
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(text.splitlines(), dialect))
    if not rows:
        msg["import_err"] = "CSV 为空或无法解析"
        return
    headers = rows[0]
    user_col = _find_col(headers, ["user name", "username", "user_name",
                                   "student id", "studentid", "学号"])
    name_col = _find_col(headers, ["first name", "firstname", "first_name",
                                   "name", "姓名"])
    if user_col is None or name_col is None:
        msg["import_err"] = (
            "未找到需要的列（User Name 与 First Name）。当前表头："
            + " | ".join(headers))
        return

    pending = []
    duplicates = []
    seen = set()
    for row in rows[1:]:
        if len(row) <= max(user_col, name_col):
            continue
        uname = row[user_col].strip()
        name = row[name_col].strip()
        if not uname or not name:
            continue
        if uname in seen or User.objects.filter(username=uname).exists():
            duplicates.append(uname)
        else:
            seen.add(uname)
            pending.append((uname, name))

    if duplicates:
        msg["import_err"] = (
            "检测到 %d 个学号已存在账号，本次未导入任何学生：%s"
            % (len(duplicates), "、".join(duplicates)))
        return

    created = []
    try:
        with transaction.atomic():
            for uname, name in pending:
                pwd = _new_random_pwd()
                u = User.objects.create_user(username=uname, password=pwd,
                                             first_name=name)
                UserProfile.objects.create(user=u, must_change_password=True)
                created.append({"username": uname, "name": name, "password": pwd})
    except IntegrityError:
        # race with a concurrent import: nothing was committed, report cleanly
        msg["import_err"] = "导入过程中检测到重复账号（可能重复提交），本次未写入任何学生，请刷新后重试"
        return
    msg["imp_created"] = len(created)
    msg["imported"] = created
    # keep this batch's initial passwords so the admin can download them once
    request.session["imported_pwds"] = created


def _pwd_csv_response(rows, prefix="initial_pwds") -> HttpResponse:
    """Render rows (username/name/password) as a UTF-8 CSV download."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["学号", "姓名", "初始密码"])
    for row in rows:
        writer.writerow([row["username"], row["name"], row["password"]])
    content = "\ufeff" + buf.getvalue()  # BOM so Excel opens UTF-8 correctly
    resp = HttpResponse(content, content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = (
        'attachment; filename="%s_%s.csv"'
        % (prefix, datetime.now().strftime("%y%m%d_%H%M")))
    return resp


def export_import_pwds(request: HttpRequest):
    """Download the last imported batch's initial passwords as a CSV file."""
    pk, r = checkcookies(request)
    if r:
        return r
    rows = request.session.pop("imported_pwds", None)
    if not rows:
        return redirect("/admin/manage_student")
    return _pwd_csv_response(rows, prefix="initial_pwds")


def stuInfoDict() -> dict:
    ret = {}
    users = User.objects.filter(is_staff=False).order_by("username")
    ret["stuNum"] = users.count()
    students = {}
    for u in users:
        students[u.pk] = {"studentID": u.username, "name": u.first_name}
    ret["students"] = students
    return ret


def check_manage_error(err: str):
    e: str
    if err == None:
        e = None
    elif err == "ME_S_A1":
        e = "学号或姓名不能为空"
    elif err == "ME_S_A2":
        e = "学号须为 5-12 位纯数字"
    elif err == "ME_S_A3":
        e = "该学号已存在账号"
    elif err == "ME_S_M1":
        e = "姓名不能为空"
    elif err == "ME_S_M2":
        e = "该学生账号不存在"
    elif err == "ME_S_D1":
        e = "您未选中任何学生"
    elif err == "ME_S_P1":
        e = "您未选中任何学生"
    else:
        e = "意外错误"
    return e
