# gym_app/views.py
# Author: Haocheng Liu <easonlhc@bu.edu>
# Description: This file contains Django view classes and functions for handling user interactions,
#              including authentication, profile management, workout sessions, fitness metrics,
#              suggestions, friendships, and messaging.

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db import models
from django.contrib.auth.models import User
from .forms import (
    RegistrationForm, ProfileForm, WorkoutSessionForm,
    FitnessMetricForm, SuggestionForm, WorkoutTypeForm, DataFilterForm, MessageForm
)
from .models import (
    Profile, WorkoutSession, WorkoutType,
    FitnessMetric, Suggestion, MemberData, Message
)
import plotly.express as px
import pandas as pd
from django.db.models import Q  # For complex queries


class HomeView(LoginRequiredMixin, TemplateView):
    """
    Home page view that displays a welcome message, suggestions, recent workout sessions,
    and data visualizations based on member data.
    """
    template_name = 'gym_app/home.html'
    login_url = reverse_lazy('login')  # Redirect to login page if not authenticated

    def get_context_data(self, **kwargs):
        """
        Adds context data to the template, including profile information, suggestions,
        recent workout sessions, and generated graphs based on filtered member data.
        """
        context = super().get_context_data(**kwargs)

        # Initialize the filter form with GET parameters or defaults.
        form = DataFilterForm(self.request.GET or None)
        context['filter_form'] = form

        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
            except Profile.DoesNotExist:
                profile = None
            context['profile'] = profile

            # Retrieve suggestions related to the user's profile.
            suggestions = Suggestion.objects.filter(profile=profile)
            context['suggestions'] = suggestions

            # Retrieve the five most recent workout sessions for the user's profile.
            recent_workout_sessions = WorkoutSession.objects.filter(
                profile=profile).order_by('-session_date')[:5]
            context['recent_workout_sessions'] = recent_workout_sessions

        else:
            context['profile'] = None
            context['suggestions'] = None
            context['recent_workout_sessions'] = None

        # Data visualization section using MemberData model.
        member_data_qs = MemberData.objects.all()

        # Apply filter conditions based on the filter form's validated data.
        if form.is_valid():
            gender = form.cleaned_data.get('gender')
            min_age = form.cleaned_data.get('min_age')
            max_age = form.cleaned_data.get('max_age')
            experience_level = form.cleaned_data.get('experience_level')
            workout_frequency = form.cleaned_data.get('workout_frequency')

            if gender and gender != 'All':
                member_data_qs = member_data_qs.filter(gender=gender)

            if min_age is not None:
                member_data_qs = member_data_qs.filter(age__gte=min_age)

            if max_age is not None:
                member_data_qs = member_data_qs.filter(age__lte=max_age)

            if experience_level and experience_level != 'All':
                member_data_qs = member_data_qs.filter(experience_level=int(experience_level))

            if workout_frequency and workout_frequency != 'All':
                if workout_frequency == 'Low':
                    member_data_qs = member_data_qs.filter(workout_frequency__lte=2)
                elif workout_frequency == 'High':
                    member_data_qs = member_data_qs.filter(workout_frequency__gte=3)

        # Proceed only if there is data after applying filters.
        if member_data_qs.exists():
            # Convert queryset to a list of dictionaries and then to a DataFrame for Plotly.
            data_list = list(member_data_qs.values())
            df = pd.DataFrame(data_list)

            # Chart 1: Scatter plot showing relationship between BMI and Workout Frequency by Gender.
            fig1 = px.scatter(df, x='bmi', y='workout_frequency', color='gender',
                              title='Workout Frequency vs BMI by Gender',
                              labels={'bmi': 'BMI', 'workout_frequency': 'Workout Frequency (days/week)'})
            graph1 = fig1.to_html(full_html=False)

            # Chart 2: Bar chart showing average BMI by age group.
            df['age_group'] = pd.cut(df['age'], bins=[0, 20, 30, 40, 50, 60, 100],
                                     labels=['0-20', '21-30', '31-40', '41-50', '51-60', '60+'])
            avg_bmi_age = df.groupby('age_group')['bmi'].mean().reset_index()
            fig2 = px.bar(avg_bmi_age, x='age_group', y='bmi', color='age_group',
                          title='Average BMI by Age Group',
                          labels={'age_group': 'Age Group', 'bmi': 'Average BMI'},
                          text_auto=True)
            graph2 = fig2.to_html(full_html=False)

            # Chart 3: Pie chart showing distribution of workout types.
            workout_type_counts = df['workout_type'].value_counts().reset_index()
            workout_type_counts.columns = ['workout_type', 'count']
            fig3 = px.pie(workout_type_counts, names='workout_type', values='count',
                          title='Distribution of Workout Types',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            graph3 = fig3.to_html(full_html=False)

            # Chart 4: Bar chart comparing average BMI for different workout frequency groups.
            df['frequency_group'] = df['workout_frequency'].apply(
                lambda x: '≤2 times/week' if x <= 2 else '≥3 times/week')
            avg_bmi_by_frequency = df.groupby('frequency_group')['bmi'].mean().reset_index()
            fig4 = px.bar(avg_bmi_by_frequency, x='frequency_group', y='bmi', color='frequency_group',
                          title='Average BMI by Workout Frequency',
                          labels={'frequency_group': 'Workout Frequency Group', 'bmi': 'Average BMI'},
                          text_auto=True,
                          color_discrete_sequence=px.colors.qualitative.Set2)
            graph4 = fig4.to_html(full_html=False)

            # Chart 5: Bar chart showing average calories burned by gender.
            avg_calories_by_gender = df.groupby('gender')['calories_burned'].mean().reset_index()
            fig5 = px.bar(avg_calories_by_gender, x='gender', y='calories_burned', color='gender',
                          title='Average Calories Burned by Gender',
                          labels={'gender': 'Gender', 'calories_burned': 'Average Calories Burned'},
                          text_auto=True,
                          color_discrete_sequence=px.colors.qualitative.Set1)
            graph5 = fig5.to_html(full_html=False)

            # Add the generated graphs to the context to be rendered in the template.
            context['graph1'] = graph1
            context['graph2'] = graph2
            context['graph3'] = graph3
            context['graph4'] = graph4
            context['graph5'] = graph5

        else:
            # If no data exists after filtering, set graph variables to None.
            context['graph1'] = None
            context['graph2'] = None
            context['graph3'] = None
            context['graph4'] = None
            context['graph5'] = None

        return context


class LoginView(AuthLoginView):
    """
    Handles user login using Django's built-in authentication views.
    Specifies the template to render for the login page.
    """
    template_name = 'gym_app/login.html'

    def get_success_url(self):
        """
        Redirects users to the home page upon successful login.
        """
        return reverse_lazy('home')


def logout_view(request):
    """
    Logs out the current user and redirects them to the login page.
    """
    logout(request)
    return redirect('login')  # Redirect to login page after logout


class RegisterView(View):
    """
    Handles user registration by rendering and processing the registration form.
    Combines user creation and profile creation in a single view.
    """
    def get(self, request):
        """
        Renders the registration form if the user is not authenticated.
        Redirects authenticated users to the home page.
        """
        if request.user.is_authenticated:
            return redirect('home')  # Redirect authenticated users to home
        user_form = RegistrationForm()
        profile_form = ProfileForm()
        return render(request, 'gym_app/register.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request):
        """
        Processes the registration form submission.
        Creates a new user and associated profile if the form is valid.
        """
        user_form = RegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # Include request.FILES for photo uploads
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()  # Save the new user.
            profile = profile_form.save(commit=False)
            profile.user = user  # Link the profile to the newly created user.
            profile.save()  # Save the profile.
            login(request, user)  # Log the user in.
            return redirect('home')  # Redirect to home page after successful registration.
        # If the form is invalid, re-render the page with existing information and errors.
        return render(request, 'gym_app/register.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })


class ProfileCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create their profile.
    Redirects to the profile detail page upon successful creation.
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'gym_app/profile_create.html'
    login_url = reverse_lazy('login')  # Redirect to login page if not authenticated.

    def form_valid(self, form):
        """
        Sets the user of the profile to the currently logged-in user before saving.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the profile detail page of the newly created profile.
        """
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a user's profile.
    Shows additional information if the viewer is a friend or the profile owner.
    """
    model = Profile
    template_name = 'gym_app/profile_detail.html'
    context_object_name = 'profile'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        """
        Adds additional context to the profile detail template, such as friendship status,
        fitness metrics, suggestions, and workout sessions.
        """
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        current_user_profile = self.request.user.profile
        is_friend = current_user_profile.is_friend(profile)
        is_self = current_user_profile == profile
        context['is_friend'] = is_friend
        context['is_self'] = is_self

        if is_friend or is_self:
            # If the viewer is a friend or the owner, display full profile details.
            fitness_metric = FitnessMetric.objects.filter(profile=profile).first()
            suggestions = Suggestion.objects.filter(profile=profile)
            workout_sessions = WorkoutSession.objects.filter(profile=profile)
            context.update({
                'fitness_metric': fitness_metric,
                'suggestions': suggestions,
                'workout_sessions': workout_sessions,
            })
        else:
            # If not a friend or owner, display limited information.
            context['limited_view'] = True

        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows users to update their own profile.
    Ensures that only the profile owner can access the update view.
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'gym_app/profile_update.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        """
        Checks if the current user is the owner of the profile being updated.
        """
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        """
        Redirects to the profile detail page after successful update.
        """
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})


class WorkoutSessionListView(LoginRequiredMixin, ListView):
    """
    Lists all workout sessions associated with the authenticated user's profile.
    """
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_list.html'
    context_object_name = 'workout_sessions'
    login_url = 'login'

    def get_queryset(self):
        """
        Retrieves workout sessions filtered by the current user's profile.
        """
        profile = self.request.user.profile
        return WorkoutSession.objects.filter(profile=profile)

    def get_context_data(self, **kwargs):
        """
        Adds fitness metrics to the context for display in the template.
        """
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        fitness_metric = FitnessMetric.objects.filter(profile=profile).first()
        context['fitness_metric'] = fitness_metric
        return context


class WorkoutSessionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Displays detailed information about a specific workout session.
    Ensures that only the owner of the session can view its details.
    """
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_detail.html'
    context_object_name = 'workout_session'
    login_url = reverse_lazy('login')

    def test_func(self):
        """
        Checks if the current user is the owner of the workout session.
        """
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user


class WorkoutSessionCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create new workout sessions.
    Associates the session with the user's profile upon creation.
    """
    model = WorkoutSession
    form_class = WorkoutSessionForm
    template_name = 'gym_app/workoutsession_form.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Associates the new workout session with the current user's profile.
        """
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the workout session detail page after successful creation.
        """
        return reverse_lazy('workoutsession_detail', kwargs={'pk': self.object.pk})


class WorkoutSessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows users to update their own workout sessions.
    Ensures that only the session owner can access the update view.
    """
    model = WorkoutSession
    form_class = WorkoutSessionForm
    template_name = 'gym_app/workoutsession_form.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        """
        Checks if the current user is the owner of the workout session being updated.
        """
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user

    def get_success_url(self):
        """
        Redirects to the workout session detail page after successful update.
        """
        return reverse_lazy('workoutsession_detail', kwargs={'pk': self.object.pk})


class WorkoutSessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows users to delete their own workout sessions.
    Ensures that only the session owner can access the delete view.
    """
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_confirm_delete.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        """
        Checks if the current user is the owner of the workout session being deleted.
        """
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user

    def get_success_url(self):
        """
        Redirects to the workout session list page after successful deletion.
        """
        return reverse_lazy('workoutsession_list')


class WorkoutTypeCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create new workout types.
    """
    model = WorkoutType
    form_class = WorkoutTypeForm
    template_name = 'gym_app/workouttype_form.html'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        """
        Redirects to the workout type list page after successful creation.
        """
        return reverse_lazy('workouttype_list')


class WorkoutTypeListView(LoginRequiredMixin, ListView):
    """
    Lists all available workout types.
    """
    model = WorkoutType
    template_name = 'gym_app/workouttype_list.html'
    context_object_name = 'workout_types'
    login_url = reverse_lazy('login')


class FitnessMetricCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create new fitness metrics.
    Redirects to the update view if a fitness metric already exists.
    """
    model = FitnessMetric
    form_class = FitnessMetricForm
    template_name = 'gym_app/fitnessmetric_form.html'
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects to the fitness metric update view if a metric already exists for the user.
        Prevents multiple fitness metrics per user.
        """
        if FitnessMetric.objects.filter(profile=request.user.profile).exists():
            return redirect('fitnessmetric_update')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Associates the new fitness metric with the current user's profile.
        """
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the workout session list page after successful creation.
        """
        return reverse('workoutsession_list')


class FitnessMetricUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allows users to update their existing fitness metrics.
    Ensures that only the metric owner can access the update view.
    """
    model = FitnessMetric
    form_class = FitnessMetricForm
    template_name = 'gym_app/fitnessmetric_form.html'
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        """
        Retrieves the fitness metric associated with the current user's profile.
        """
        return get_object_or_404(FitnessMetric, profile=self.request.user.profile)

    def get_success_url(self):
        """
        Redirects to the workout session list page after successful update.
        """
        return reverse('workoutsession_list')


class FitnessMetricDeleteView(LoginRequiredMixin, View):
    """
    Handles deletion of fitness metrics.
    Ensures that only the metric owner can delete their fitness metric.
    """
    login_url = reverse_lazy('login')

    def post(self, request, pk):
        """
        Deletes the specified fitness metric if the user is authorized.
        """
        fitness_metric = get_object_or_404(FitnessMetric, pk=pk, profile=request.user.profile)
        fitness_metric.delete()
        messages.success(request, 'Fitness metric deleted successfully.')
        return redirect('workoutsession_list')


class SuggestionCreateView(LoginRequiredMixin, CreateView):
    """
    Allows users to manually create suggestions.
    Typically, suggestions are auto-generated, but this view provides flexibility.
    """
    model = Suggestion
    form_class = SuggestionForm
    template_name = 'gym_app/suggestion_form.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Associates the new suggestion with the current user's profile before saving.
        """
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the suggestion list page after successful creation.
        """
        return reverse_lazy('suggestion_list')


class SuggestionListView(LoginRequiredMixin, ListView):
    """
    Lists all suggestions associated with the authenticated user's profile.
    """
    model = Suggestion
    template_name = 'gym_app/suggestion_list.html'
    context_object_name = 'suggestions'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        """
        Retrieves suggestions filtered by the current user's profile.
        """
        return Suggestion.objects.filter(profile=self.request.user.profile)


class AddFriendView(LoginRequiredMixin, View):
    """
    Handles the addition of a friend.
    Ensures that users cannot add themselves and that friendships are unique.
    """
    login_url = 'login'

    def post(self, request, pk):
        """
        Adds the specified profile as a friend if conditions are met.
        """
        current_user_profile = request.user.profile
        other_profile = get_object_or_404(Profile, pk=pk)
        if current_user_profile != other_profile:
            if not current_user_profile.is_friend(other_profile):
                current_user_profile.add_friend(other_profile)
                messages.success(request, f"You are now friends with {other_profile.user.username}.")
            else:
                messages.info(request, f"You are already friends with {other_profile.user.username}.")
        else:
            messages.error(request, "You cannot add yourself as a friend.")
        return redirect('friend_list')


class RemoveFriendView(LoginRequiredMixin, View):
    """
    Handles the removal of a friend.
    Ensures that only existing friends can be removed.
    """
    login_url = 'login'

    def post(self, request, pk):
        """
        Removes the specified profile from the user's friends.
        """
        current_user_profile = request.user.profile
        other_profile = get_object_or_404(Profile, pk=pk)
        if current_user_profile.is_friend(other_profile):
            current_user_profile.remove_friend(other_profile)
            messages.success(request, f"You have removed {other_profile.user.username} from your friends.")
        else:
            messages.error(request, f"{other_profile.user.username} is not in your friends list.")
        return redirect('friend_list')


class FriendListView(LoginRequiredMixin, ListView):
    """
    Lists all friends associated with the authenticated user's profile.
    """
    template_name = 'gym_app/friend_list.html'
    context_object_name = 'friends'
    login_url = 'login'

    def get_queryset(self):
        """
        Retrieves the list of friends for the current user's profile.
        """
        profile = self.request.user.profile
        return profile.get_friends()


class AddFriendListView(LoginRequiredMixin, ListView):
    """
    Displays a list of profiles that can be added as friends.
    Excludes current user and existing friends.
    """
    template_name = 'gym_app/add_friend_list.html'
    context_object_name = 'profiles'
    login_url = 'login'

    def get_queryset(self):
        """
        Retrieves profiles excluding the current user and their existing friends.
        """
        current_user_profile = self.request.user.profile
        friends = current_user_profile.get_friends()
        excluded_profiles = [current_user_profile] + friends
        return Profile.objects.exclude(id__in=[p.id for p in excluded_profiles])


@login_required
def send_message(request, recipient_id):
    """
    Handles sending a message to another user.
    Ensures that the recipient is a friend of the sender.
    """
    recipient = get_object_or_404(User, id=recipient_id)
    # Check if the sender and recipient are friends.
    if not request.user.profile.is_friend(recipient.profile):
        return HttpResponseForbidden("You can only send messages to your friends.")
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Create a new Message instance without saving to the database yet.
            new_message = form.save(commit=False)
            new_message.sender = request.user  # Set the sender to the current user.
            new_message.recipient = recipient  # Set the recipient.
            new_message.save()  # Save the message to the database.
            messages.success(request, 'Message sent successfully.')
            return redirect('message_thread', user_id=recipient.id)
    else:
        form = MessageForm()
    return render(request, 'gym_app/send_message.html', {'form': form, 'recipient': recipient})


@login_required
def message_thread(request, user_id):
    """
    Displays the conversation thread between the current user and another user.
    Handles sending new messages within the thread.
    Ensures that the users are friends.
    """
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return HttpResponseForbidden("You cannot message yourself.")
    if not request.user.profile.is_friend(other_user.profile):
        return HttpResponseForbidden("You can only view conversations with your friends.")

    # Retrieve all messages between the current user and the other user, ordered by timestamp.
    messages_qs = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Create a new Message instance without saving to the database yet.
            new_message = form.save(commit=False)
            new_message.sender = request.user  # Set the sender to the current user.
            new_message.recipient = other_user  # Set the recipient.
            new_message.save()  # Save the message to the database.
            return redirect('message_thread', user_id=other_user.id)
    else:
        form = MessageForm()
    return render(request, 'gym_app/message_thread.html', {
        'chat_messages': messages_qs,  # Pass the messages to the template.
        'other_user': other_user,  # Pass the other user's information.
        'form': form,  # Pass the message form to the template.
    })


@login_required
def delete_message(request, message_id):
    """
    Handles deletion of a message.
    Ensures that only the sender can delete their own messages.
    """
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You cannot delete this message.")
    if request.method == 'POST':
        message.delete()  # Delete the message from the database.
        messages.success(request, 'Message deleted successfully.')
        return redirect('message_thread', user_id=message.recipient.id)
    return render(request, 'gym_app/delete_message.html', {'message_obj': message})


@login_required
def update_message(request, message_id):
    """
    Handles updating/editing of a message.
    Ensures that only the sender can edit their own messages.
    """
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You cannot edit this message.")
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()  # Save the updated message to the database.
            messages.success(request, 'Message updated successfully.')
            return redirect('message_thread', user_id=message.recipient.id)
    else:
        form = MessageForm(instance=message)  # Pre-fill the form with existing message content.
    return render(request, 'gym_app/update_message.html', {'form': form, 'message_obj': message})


class ChatListView(LoginRequiredMixin, TemplateView):
    """
    Displays a list of all chat conversations the user is involved in.
    Shows friends and recent conversation threads.
    """
    template_name = 'gym_app/chat_list.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        """
        Adds context data including the user's friends and sorted conversations based on the latest message.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Retrieve all friends of the current user.
        profile = user.profile
        friends = profile.get_friends()
        context['friends'] = friends

        # Retrieve all messages where the user is either the sender or recipient.
        messages_qs = Message.objects.filter(Q(sender=user) | Q(recipient=user))
        conversations = {}

        # Iterate through messages to identify unique conversation partners.
        for message in messages_qs:
            # Determine the other user in the conversation.
            if message.sender == user:
                other_user = message.recipient
            else:
                other_user = message.sender
            # Update the latest timestamp for each conversation.
            if other_user in conversations:
                if conversations[other_user] < message.timestamp:
                    conversations[other_user] = message.timestamp
            else:
                conversations[other_user] = message.timestamp

        # Sort conversations based on the latest message timestamp in descending order.
        conversations = sorted(conversations.items(), key=lambda x: x[1], reverse=True)
        # Extract the sorted list of users involved in conversations.
        context['conversations'] = [user for user, _ in conversations]
        return context
