from django.shortcuts import render

def index(request):
    context = {}
    return render(request, "mainApp/index.html", context)