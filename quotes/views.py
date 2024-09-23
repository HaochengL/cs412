from django.shortcuts import render
import random

# Updated quotes - all by Albert Einstein
quotes = [
    {"quote": "Life is like riding a bicycle. To keep your balance, you must keep moving.", "author": "Albert Einstein"},
    {"quote": "Imagination is more important than knowledge. For knowledge is limited, whereas imagination embraces the entire world.", "author": "Albert Einstein"},
    {"quote": "Strive not to be a success, but rather to be of value.", "author": "Albert Einstein"},
    {"quote": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
]


images = [
    "https://astrumpeople.com/wp-content/uploads/2016/06/Albert-Einstein-1-768x768.jpeg",
    "https://www.publicdomainpictures.net/pictures/520000/velka/albert-einstein-1685961420x7b.jpg",
    "https://www.muraldecal.com/en/img/as645-jpg/folder/products-listado-merchant/wall-stickers-albert-einstein.jpg",
    "https://images.fineartamerica.com/images/artworkimages/medium/3/albert-einstein-painting-mark-ashkenazi.jpg"
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

    person_info = "Albert Einstein was a theoretical physicist widely acknowledged for developing the theory of relativity, but also known for his insightful thoughts on life and imagination."
    bio = "The quotes displayed here are all from Albert Einstein, who believed in the power of imagination and the importance of curiosity."

    context = {
    'bio': bio,
    'person_info': person_info
    }

    return render(request, template_name, context)