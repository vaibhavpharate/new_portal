from django.shortcuts import render
import pandas as pd
import numpy as np
# Create your views here.


def home_screen(request):
    return render(request=request,template_name='home.html')
