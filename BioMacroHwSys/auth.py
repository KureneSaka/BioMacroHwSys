# -*- coding: utf-8 -*-
"""Central authentication helpers (normal site style).

Accounts are django.contrib.auth.User instances:
  - students: is_staff=False, username = student id (digits)
  - admins:   is_staff=True,  username = login name
"""
from django.shortcuts import redirect

from App_dataSystem.models import UserProfile

# Paths that must stay reachable while must_change_password is set
# (otherwise the forced redirect would loop).
CHANGE_PWD_PATHS = ("/student/change_pwd", "/admin/change_pwd")


def is_admin(user) -> bool:
    return bool(user.is_authenticated and user.is_staff)


def is_student(user) -> bool:
    return bool(user.is_authenticated and not user.is_staff)


def student_sid(user) -> int:
    """Return the student id (int) derived from a student's username."""
    try:
        return int(user.username)
    except (TypeError, ValueError):
        return 0


def must_change_password(user) -> bool:
    if not user.is_authenticated:
        return False
    return UserProfile.objects.filter(
        user=user, must_change_password=True).exists()


def pwd_url(user) -> str:
    return "/admin/change_pwd" if is_admin(user) else "/student/change_pwd"


def force_pwd_redirect(user):
    """Return a redirect to the change-password page, or None if not forced."""
    if must_change_password(user):
        return redirect(pwd_url(user))
    return None
