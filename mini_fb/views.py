# views.py
# Author: Haocheng Liu
# Username: easonlhc@bu.edu
# Description: This file defines the views for the mini Facebook application.
#              It includes views to display all profiles, show a single profile's details, 
#              create a new profile, and create status messages for a profile.

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse
from .models import Profile
from .forms import CreateProfileForm, CreateStatusMessageForm

class ShowAllProfilesView(ListView):
    """
    Displays a list of all profiles.

    Attributes:
    model (Model): The Profile model.
    template_name (str): The template used to render the view.
    context_object_name (str): The name of the context variable containing the profiles.
    """
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    """
    Displays the details of a single profile.

    Attributes:
    model (Model): The Profile model.
    template_name (str): The template used to render the profile detail view.
    """
    model = Profile
    template_name = 'mini_fb/show_profile.html'

class CreateProfileView(CreateView):
    """
    Handles the creation of a new profile.

    Attributes:
    form_class (Form): The form class used to create a new profile.
    template_name (str): The template used to render the profile creation form.
    """
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

class CreateStatusMessageView(CreateView):
    """
    Handles the creation of a new status message for a specific profile.

    Attributes:
    form_class (Form): The form class used to create a new status message.
    template_name (str): The template used to render the status creation form.
    """

    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        """
        Adds the profile to the context, allowing access to the profile within the template.

        Parameters:
        **kwargs: Additional context arguments.

        Returns:
        dict: The updated context dictionary with the profile.
        """
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """
        Associates the new status message with the profile and validates the form.

        Parameters:
        form (Form): The form instance being validated.

        Returns:
        HttpResponse: The response to the valid form submission.
        """
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the profile page after successfully creating a status message.

        Returns:
        str: The URL to the profile detail page.
        """
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
