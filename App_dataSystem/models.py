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
    seconded = models.IntegerField(default=0)  # 附议次数
    disliked = models.IntegerField(default=0)  # 点踩次数
    studentID = models.IntegerField()  # 提问人学号
    submitTime = models.DateTimeField(auto_now_add=True)  # 提交时间
    finalscore = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)  # 最终得分


class quesResponseDB(models.Model):
    quesID = models.IntegerField()  # question pk
    response = models.TextField()
    responderType = models.CharField(
        max_length=1, choices=[("A", "admin"), ("S", "student")])
    responderID = models.IntegerField()  # responder pk
    respondTime = models.DateTimeField(auto_now=True)


class quesEvaluateDB(models.Model):
    quesID = models.IntegerField()  # question pk
    studentID = models.IntegerField()  # seconder pk
    evaluation = models.CharField(
        max_length=1, choices=[("S", "seconded"), ("N", "none"), ("D", "dislike")], default="N")
