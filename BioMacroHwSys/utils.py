from django.http import HttpRequest, HttpResponse, QueryDict
import time


def outputPost(request: HttpRequest):
    print("------[" + time.strftime('%d/%h/%Y %H:%M:%S') +
          "] Got a post from \"" + request.path + "\", POST is: ")
    print(request.POST)


def outputMsg(msg: dict):
    print("------[" + time.strftime('%d/%h/%Y %H:%M:%S') +
          "] Ready to send a response with msg: ")
    print(msg)
