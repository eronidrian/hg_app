from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("HG webová aplikace. Alfa verze.")

