from django.db import models

# Create your models here.


class stuBaseInfo(models.Model):
    studentID = models.IntegerField()
    name = models.CharField(max_length=10)
    hash = models.CharField(max_length=10)


class adminBaseInfo(models.Model):
    name = models.CharField(max_length=10)
    hash = models.CharField(max_length=10)


class quesBaseInfo(models.Model):
    question = models.TextField()  # 问题
    visible = models.BooleanField(default=True)
    seconded = models.IntegerField(default=0)  # 附议次数
    disliked = models.IntegerField(default=0)  # 点踩次数
    studentID = models.IntegerField()  # 提问人学号
    submitTime = models.DateTimeField(auto_now_add=True)  # 提交时间
    week = models.IntegerField() #周次pk
    adminsuconded = models.BooleanField(default=False)
    admindisliked = models.BooleanField(default=False)


class quesResponseDB(models.Model):
    quesID = models.IntegerField()  # question pk
    responded = models.BooleanField(default=True)
    response = models.TextField(blank=True)
    responderType = models.CharField(
        max_length=1, choices=[("A", "admin"), ("S", "student")])
    responderID = models.IntegerField()  # responder id
    respondTime = models.DateTimeField(auto_now=True)
    week = models.IntegerField()  # 周次pk


class quesEvaluateDB(models.Model):
    quesID = models.IntegerField()  # question pk
    studentID = models.IntegerField()  # seconder pk
    evaluation = models.CharField(
        max_length=1, choices=[("S", "seconded"), ("N", "none"), ("D", "dislike")], default="N")


class weekDB(models.Model):
    week = models.IntegerField() #周次数字
    lectureBegin = models.IntegerField() #开始章节
    lectureFinish = models.IntegerField() #结束章节
    timeBegin = models.DateTimeField()
    timeSubmitFinish = models.DateTimeField()
    timeEvaluateFinish = models.DateTimeField()
