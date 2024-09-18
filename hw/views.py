import time
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random
# Create your views here.

def home(request):
    template_name = "hw/home.html"

    context ={
        'current_time': time.ctime(),
        'letter1': chr(random.randint(65,90)),
        'letter2': chr(random.randint(65,90)),
        'number': random.randint(1,10),
    }

    return render(request, template_name, context)

##def home(request):

    
    '''A function to respond to the /hw url'''

    response_text = f'''
    <html>
    <h1>Hello, world!</h1>
    <p>
    This is our first django web page!
    </p>
    <hr>
    This page was generated at {time.ctime()}.

    '''

    return HttpResponse(
        response_text)
