from django.shortcuts import render  # NOQA
from django.http import HttpResponse


# Create your views here.

def home(request):
    """Displaying the home page"""
    return HttpResponse('Hello, World!')
