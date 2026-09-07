from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """Extra flags attached to a django.contrib.auth User account.

    User accounts now carry all login data (username/password), so the old
    stuBaseInfo/adminBaseInfo name lists are gone:
      - student accounts: is_staff=False, username = student id (digits)
      - admin accounts:   is_staff=True,  username = login name
    This profile only stores non-auth extras, e.g. "must change password".
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    must_change_password = models.BooleanField(default=False)


class quesBaseInfo(models.Model):
    question = models.TextField()  # 问题
    visible = models.BooleanField(default=True)
    seconded = models.IntegerField(default=0)  # 附议次数
    disliked = models.IntegerField(default=0)  # 点踩次数
    # 提问人学号（即 User.username）。刻意不用外键：删除账号后历史问题保留并显示“未知”
    studentID = models.IntegerField(db_index=True)
    submitTime = models.DateTimeField(auto_now_add=True)  # 提交时间
    week = models.IntegerField(db_index=True)  # 周次 pk（引用 weekDB）
    adminseconded = models.BooleanField(default=False)
    admindisliked = models.BooleanField(default=False)


class quesResponseDB(models.Model):
    quesID = models.IntegerField(db_index=True)  # question pk
    responded = models.BooleanField(default=True)
    response = models.TextField(blank=True)
    responderType = models.CharField(
        max_length=1, choices=[("A", "admin"), ("S", "student")])
    # 回答者：A=管理员 User pk，S=学生学号（User.username）。无外键：保持与历史数据/删除策略一致
    responderID = models.IntegerField(db_index=True)
    respondTime = models.DateTimeField(auto_now=True)
    week = models.IntegerField(db_index=True)  # 周次 pk


class quesEvaluateDB(models.Model):
    quesID = models.IntegerField(db_index=True)  # question pk
    studentID = models.IntegerField(db_index=True)  # 评价人学号（User.username）
    evaluation = models.CharField(
        max_length=1, choices=[("S", "seconded"), ("N", "none"), ("D", "dislike")], default="N")


class weekDB(models.Model):
    week = models.IntegerField(unique=True)  # 周次数字（唯一：切换周次时按此反查）
    lectureBegin = models.IntegerField()  # 开始章节
    lectureFinish = models.IntegerField() #结束章节
    timeBegin = models.DateTimeField()
    timeSubmitFinish = models.DateTimeField()
    timeEvaluateFinish = models.DateTimeField()
