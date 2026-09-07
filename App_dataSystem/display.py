# -*- coding: utf-8 -*-
"""Shared display helpers for questions/results.

These used to live inside App_adminSystem.views.utils (which the export
module imported directly, creating a reverse App_exportfile -> admin-views
dependency). Keeping them in the data layer lets the admin UI, the export
module and the docx generator all share one implementation.
"""
from django.contrib.auth.models import User

from App_dataSystem.models import quesBaseInfo, quesResponseDB


def stuid2name(id: int) -> str:
    """Student display name by student id (stored as User.username)."""
    try:
        return User.objects.get(username=str(id)).first_name
    except User.DoesNotExist:
        return "未知"


def pk2name(pk: int) -> str:
    """Admin display name by admin User pk."""
    try:
        return User.objects.get(pk=pk).first_name
    except User.DoesNotExist:
        return "未知"


def getallresponses(pk: int):
    return quesResponseDB.objects.filter(quesID=pk, responded=True)


def quesList2dict(quesList) -> dict:
    """Build the display/export dict for a list of questions.

    Full ("admin") view: includes the asker name and responder names, the
    soft-delete flag and the admin like/dislike flags.
    """
    questions = {}
    cnt = 0
    for i in quesList:
        q = {}
        try:
            q["asker"] = stuid2name(i.studentID)
        except Exception:
            q["asker"] = "未知"
        q["seconded"] = i.seconded
        q["disliked"] = i.disliked
        q["question"] = i.question
        q["date"] = i.submitTime.strftime("%y/%m/%d")
        q["time"] = i.submitTime.strftime("%H:%M")
        q["visible"] = i.visible
        q["adminseconded"] = i.adminseconded
        q["admindisliked"] = i.admindisliked
        respList = getallresponses(i.pk)
        responses = {}
        for j in respList:
            r = {}
            r["adminrespond"] = True if j.responderType == "A" else False
            try:
                r["responder"] = pk2name(
                    j.responderID) if r["adminrespond"] else stuid2name(j.responderID)
            except Exception:
                r["responder"] = "未知"
            r["response"] = j.response
            r["date"] = j.respondTime.strftime("%y/%m/%d")
            r["time"] = j.respondTime.strftime("%H:%M")
            responses[j.pk] = r
        q["rowNum"] = len(responses) + 1
        q["responses"] = responses
        cnt = cnt + 1
        q["cnt"] = cnt
        questions[i.pk] = q
    return questions
