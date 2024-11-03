# mini_fb/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from .models import Profile, StatusMessage, Image
from .forms import (
    CreateProfileForm, 
    CreateStatusMessageForm, 
    UpdateProfileForm, 
    UpdateStatusMessageForm,
    UserRegistrationForm,
)

class ShowAllProfilesView(ListView):
    """Display a list of all Profiles."""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'


class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # Retrieve the profile based on pk in the URL
        return get_object_or_404(Profile, pk=self.kwargs['pk'])


class CreateProfileView(FormView):
    """Handle user registration and profile creation."""
    template_name = 'mini_fb/create_profile_form.html'
    form_class = UserRegistrationForm

    def get_context_data(self, **kwargs):
        """Add CreateProfileForm to the context."""
        context = super().get_context_data(**kwargs)
        context['profile_form'] = CreateProfileForm(self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        """Process both UserRegistrationForm and CreateProfileForm."""
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            # Create the User
            user = form.save()
            # Create the Profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # Log the user in
            login(self.request, user)
            self.profile = profile  # Store the profile for success URL
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        """Redirect to the new profile page."""
        return reverse('show_profile', kwargs={'pk': self.profile.pk})


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """Allow users to update their own Profile."""
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Retrieve the Profile associated with the logged-in user."""
        return self.request.user.profile

    def get_success_url(self):
        """Redirect to the Profile page after successful update."""
        return reverse('show_profile', kwargs={'pk': self.object.pk})


class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    """Allow users to create a new StatusMessage."""
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def form_valid(self, form):
        """Associate the StatusMessage with the user's Profile and handle image uploads."""
        form.instance.profile = self.request.user.profile
        response = super().form_valid(form)
        files = self.request.FILES.getlist('files')
        for f in files:
            Image.objects.create(status_message=self.object, image_file=f)
        return response

    def get_success_url(self):
        """Redirect to the Profile page after successful creation."""
        return reverse('show_profile', kwargs={'pk': self.request.user.profile.pk})


class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow users to update their own StatusMessages."""
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status'

    def test_func(self):
        """Ensure that the user owns the StatusMessage."""
        status = self.get_object()
        return self.request.user == status.profile.user

    def get_success_url(self):
        """Redirect to the Profile page after successful update."""
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})


class DeleteStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allow users to delete their own StatusMessages."""
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status'

    def test_func(self):
        """Ensure that the user owns the StatusMessage."""
        status = self.get_object()
        return self.request.user == status.profile.user

    def get_success_url(self):
        """Redirect to the Profile page after successful deletion."""
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})


class CreateFriendView(LoginRequiredMixin, View):
    """Handle the addition of a new friend."""

    def post(self, request, other_pk, *args, **kwargs):
        """Process the friend addition."""
        profile = self.request.user.profile
        other_profile = get_object_or_404(Profile, pk=other_pk)
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)


class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    """Display friend suggestions for the logged-in user."""
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Retrieve the Profile associated with the logged-in user."""
        return self.request.user.profile


class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    """Display the news feed for the logged-in user."""
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Retrieve the Profile associated with the logged-in user."""
        return self.request.user.profile
