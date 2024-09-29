from django.shortcuts import render, redirect
import random
import datetime


# Main page view
def main_page(request):
    template_name = 'restaurant/main.html'

    context = {
        'name': 'Futago',
        'location': '508-512 Park Dr, Boston, MA 02115',
        'hours': [
            {'day': 'Monday', 'time': 'Closed'},
            {'day': 'Tuesday', 'time': '12 AM - 8:30 PM'},
            {'day': 'Wednesday', 'time': '12 AM - 8:30 PM'},
            {'day': 'Thursday', 'time': '12 AM - 8:30 PM'},
            {'day': 'Friday', 'time': '12 AM - 8:30 PM'},
            {'day': 'Saturday', 'time': '12 AM - 8:30 PM'},
            {'day': 'Sunday', 'time': '12 AM - 8:30 PM'},
        ],
        'images': ['https://s3-media0.fl.yelpcdn.com/bphoto/gW6jXkrvc-aBZEpisyTWfw/o.jpg'],
    }

    return render(request, template_name, context)


# Order page view
def order(request):
    menu_items = {
        'Sukiyaki Udon': 24.00,
        'Uni Cream Udon': 25.00,
        'Takoyaki': 9.00,
        'Pork Kimchi Udon': 20.00,
    }
    daily_special = random.choice(list(menu_items.items()))  # Randomly select daily special

    if request.method == 'POST':
        # Get form data
        selected_items = request.POST.getlist('items')
        customer_name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        special_instructions = request.POST.get('instructions')

        # Initialize the total price
        total_price = 0

        # Calculate total price based on selected items
        for item in selected_items:
            total_price += menu_items[item]  # Add the price of each selected item

        # Check if the user selected extra options for Takoyaki
        takoyaki_options = request.POST.getlist('takoyaki_options')
        if 'Takoyaki' in selected_items and 'Extra Sauce' in takoyaki_options:
            total_price += 1  # Add $1 for extra sauce on Takoyaki

        
        # Store form data in session for confirmation view
        request.session['selected_items'] = selected_items
        request.session['total_price'] = total_price
        request.session['customer_name'] = customer_name
        request.session['phone'] = phone
        request.session['email'] = email
        request.session['instructions'] = special_instructions

        # Redirect to the confirmation page
        return redirect('confirmation')

    context = {
        'menu_items': menu_items,
        'daily_special': daily_special,
    }
    return render(request, 'restaurant/order.html', context)


# Confirmation page view
def confirmation(request):
    selected_items = request.session.get('selected_items')
    total_price = request.session.get('total_price')
    customer_name = request.session.get('customer_name')
    phone = request.session.get('phone')
    email = request.session.get('email')
    instructions = request.session.get('instructions')

    # Generate random ready time between 30 to 60 minutes
    ready_in_minutes = random.randint(30, 60)
    current_time = datetime.datetime.now()
    ready_time = current_time + datetime.timedelta(minutes=ready_in_minutes)

    context = {
        'selected_items': selected_items,
        'total_price': total_price,
        'customer_name': customer_name,
        'phone': phone,
        'email': email,
        'instructions': instructions,
        'ready_time': ready_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, 'restaurant/confirmation.html', context)
