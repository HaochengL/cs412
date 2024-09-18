from django.shortcuts import render
import random

# Create your views here.
quotes = [
    {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"quote": "Success is not how high you have climbed, but how you make a positive difference to the world.", "author": "Roy T. Bennett"},
    {"quote": "In the end, we will remember not the words of our enemies, but the silence of our friends.", "author": "Martin Luther King Jr."}
]

images = [
    "https://static9.depositphotos.com/1319000/1216/i/450/depositphotos_12164661-stock-photo-woman-with-arms-outstretched.jpg",
    "https://t3.ftcdn.net/jpg/02/52/65/60/240_F_252656083_CL2ijXn7hLLkL7zGnlsR1S2actQ3n9Wq.jpg",
    "https://t3.ftcdn.net/jpg/02/69/52/30/240_F_269523005_YdDtqmGWtdu8pmnc0hgaJDZlpR9TTSHr.jpg"
]

#main page
def quote(request):
    template_name = 'quotes/quote.html'
    selected_quote = random.choice(quotes)  # Select a random quote and author
    
    context = {
        'quote': selected_quote["quote"],
        'author': selected_quote["author"],
        'selected_image': random.choice(images),
    }

    return render(request, template_name, context)

# Show all quotes and images
def show_all(request):

    template_name = 'quotes/show_all.html'

    context = {
    'quotes': quotes,
    'images': images,
    }

    return render(request, template_name, context)

# About page
def about(request):

    template_name = 'quotes/about.html'

    person_info = "This app showcases quotes and images from a famous figure."
    bio = "The person whose quotes are displayed here is well-known for their inspiring words."

    context = {
    'bio': bio,
    'person_info': person_info
    }

    return render(request, template_name, context)