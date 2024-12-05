# gym_app/views.py

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

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'gym_app/home.html'
    login_url = reverse_lazy('login')  # Redirect to login page if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize the filter form
        form = DataFilterForm(self.request.GET or None)
        context['filter_form'] = form

        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
            except Profile.DoesNotExist:
                profile = None
            context['profile'] = profile

            # Get user's suggestions
            suggestions = Suggestion.objects.filter(profile=profile)
            context['suggestions'] = suggestions

            # Get recent workout sessions
            recent_workout_sessions = WorkoutSession.objects.filter(
                profile=profile).order_by('-session_date')[:5]
            context['recent_workout_sessions'] = recent_workout_sessions

        else:
            context['profile'] = None
            context['suggestions'] = None
            context['recent_workout_sessions'] = None

        # Data visualization section
        member_data_qs = MemberData.objects.all()

        # Apply filter conditions
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

        # Convert queryset to DataFrame
        if member_data_qs.exists():
            data_list = list(member_data_qs.values())
            df = pd.DataFrame(data_list)

            # Chart 1: Relationship between BMI and Workout Frequency by Gender
            fig1 = px.scatter(df, x='bmi', y='workout_frequency', color='gender',
                              title='Workout Frequency vs BMI by Gender',
                              labels={'bmi': 'BMI', 'workout_frequency': 'Workout Frequency (days/week)'})
            graph1 = fig1.to_html(full_html=False)

            # Chart 2: Average BMI by Age Group
            df['age_group'] = pd.cut(df['age'], bins=[0, 20, 30, 40, 50, 60, 100],
                                     labels=['0-20', '21-30', '31-40', '41-50', '51-60', '60+'])
            avg_bmi_age = df.groupby('age_group')['bmi'].mean().reset_index()
            fig2 = px.bar(avg_bmi_age, x='age_group', y='bmi', color='age_group',
                          title='Average BMI by Age Group',
                          labels={'age_group': 'Age Group', 'bmi': 'Average BMI'},
                          text_auto=True)
            graph2 = fig2.to_html(full_html=False)

            # Chart 3: Distribution of Workout Types (Pie Chart)
            workout_type_counts = df['workout_type'].value_counts().reset_index()
            workout_type_counts.columns = ['workout_type', 'count']
            fig3 = px.pie(workout_type_counts, names='workout_type', values='count',
                          title='Distribution of Workout Types',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            graph3 = fig3.to_html(full_html=False)

            # Chart 4: Compare BMI for Workout Frequency ≤2 times/week vs ≥3 times/week
            df['frequency_group'] = df['workout_frequency'].apply(
                lambda x: '≤2 times/week' if x <= 2 else '≥3 times/week')
            avg_bmi_by_frequency = df.groupby('frequency_group')['bmi'].mean().reset_index()
            fig4 = px.bar(avg_bmi_by_frequency, x='frequency_group', y='bmi', color='frequency_group',
                          title='Average BMI by Workout Frequency',
                          labels={'frequency_group': 'Workout Frequency Group', 'bmi': 'Average BMI'},
                          text_auto=True,
                          color_discrete_sequence=px.colors.qualitative.Set2)
            graph4 = fig4.to_html(full_html=False)

            # Chart 5: Average Calories Burned by Gender
            avg_calories_by_gender = df.groupby('gender')['calories_burned'].mean().reset_index()
            fig5 = px.bar(avg_calories_by_gender, x='gender', y='calories_burned', color='gender',
                          title='Average Calories Burned by Gender',
                          labels={'gender': 'Gender', 'calories_burned': 'Average Calories Burned'},
                          text_auto=True,
                          color_discrete_sequence=px.colors.qualitative.Set1)
            graph5 = fig5.to_html(full_html=False)

            context['graph1'] = graph1
            context['graph2'] = graph2
            context['graph3'] = graph3
            context['graph4'] = graph4
            context['graph5'] = graph5

        else:
            context['graph1'] = None
            context['graph2'] = None
            context['graph3'] = None
            context['graph4'] = None
            context['graph5'] = None

        return context

class LoginView(AuthLoginView):
    template_name = 'gym_app/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')  # Redirect authenticated users to home
        user_form = RegistrationForm()
        profile_form = ProfileForm()
        return render(request, 'gym_app/register.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request):
        user_form = RegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # Include request.FILES
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('home')
        return render(request, 'gym_app/register.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'gym_app/profile_create.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'gym_app/profile_detail.html'
    context_object_name = 'profile'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        current_user_profile = self.request.user.profile
        is_friend = current_user_profile.is_friend(profile)
        is_self = current_user_profile == profile
        context['is_friend'] = is_friend
        context['is_self'] = is_self

        if is_friend or is_self:
            # Show full details
            fitness_metric = FitnessMetric.objects.filter(profile=profile).first()
            suggestions = Suggestion.objects.filter(profile=profile)
            workout_sessions = WorkoutSession.objects.filter(profile=profile)
            context.update({
                'fitness_metric': fitness_metric,
                'suggestions': suggestions,
                'workout_sessions': workout_sessions,
            })
        else:
            # Limited information
            context['limited_view'] = True

        return context

class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'gym_app/profile_update.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})

class WorkoutSessionListView(LoginRequiredMixin, ListView):
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_list.html'
    context_object_name = 'workout_sessions'
    login_url = 'login'

    def get_queryset(self):
        profile = self.request.user.profile
        return WorkoutSession.objects.filter(profile=profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        fitness_metric = FitnessMetric.objects.filter(profile=profile).first()
        context['fitness_metric'] = fitness_metric
        return context

class WorkoutSessionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_detail.html'
    context_object_name = 'workout_session'
    login_url = reverse_lazy('login')

    def test_func(self):
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user

class WorkoutSessionCreateView(LoginRequiredMixin, CreateView):
    model = WorkoutSession
    form_class = WorkoutSessionForm
    template_name = 'gym_app/workoutsession_form.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('workoutsession_detail', kwargs={'pk': self.object.pk})

class WorkoutSessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WorkoutSession
    form_class = WorkoutSessionForm
    template_name = 'gym_app/workoutsession_form.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user

    def get_success_url(self):
        return reverse_lazy('workoutsession_detail', kwargs={'pk': self.object.pk})

class WorkoutSessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = WorkoutSession
    template_name = 'gym_app/workoutsession_confirm_delete.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        workout_session = self.get_object()
        return self.request.user == workout_session.profile.user

    def get_success_url(self):
        return reverse_lazy('workoutsession_list')

class WorkoutTypeCreateView(LoginRequiredMixin, CreateView):
    model = WorkoutType
    form_class = WorkoutTypeForm
    template_name = 'gym_app/workouttype_form.html'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse_lazy('workouttype_list')

class WorkoutTypeListView(LoginRequiredMixin, ListView):
    model = WorkoutType
    template_name = 'gym_app/workouttype_list.html'
    context_object_name = 'workout_types'
    login_url = reverse_lazy('login')

class FitnessMetricCreateView(LoginRequiredMixin, CreateView):
    model = FitnessMetric
    form_class = FitnessMetricForm
    template_name = 'gym_app/fitnessmetric_form.html'
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if FitnessMetric.objects.filter(profile=request.user.profile).exists():
            return redirect('fitnessmetric_update')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workoutsession_list')

class FitnessMetricUpdateView(LoginRequiredMixin, UpdateView):
    model = FitnessMetric
    form_class = FitnessMetricForm
    template_name = 'gym_app/fitnessmetric_form.html'
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return get_object_or_404(FitnessMetric, profile=self.request.user.profile)

    def get_success_url(self):
        return reverse('workoutsession_list')

class FitnessMetricDeleteView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, pk):
        fitness_metric = get_object_or_404(FitnessMetric, pk=pk, profile=request.user.profile)
        fitness_metric.delete()
        return redirect('workoutsession_list')

class SuggestionCreateView(LoginRequiredMixin, CreateView):
    model = Suggestion
    form_class = SuggestionForm
    template_name = 'gym_app/suggestion_form.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('suggestion_list')

class SuggestionListView(LoginRequiredMixin, ListView):
    model = Suggestion
    template_name = 'gym_app/suggestion_list.html'
    context_object_name = 'suggestions'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Suggestion.objects.filter(profile=self.request.user.profile)

class AddFriendView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, pk):
        current_user_profile = request.user.profile
        other_profile = get_object_or_404(Profile, pk=pk)
        if current_user_profile != other_profile:
            if not current_user_profile.is_friend(other_profile):
                current_user_profile.add_friend(other_profile)
        return redirect('friend_list')

class RemoveFriendView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, pk):
        current_user_profile = request.user.profile
        other_profile = get_object_or_404(Profile, pk=pk)
        if current_user_profile.is_friend(other_profile):
            current_user_profile.remove_friend(other_profile)
        return redirect('friend_list')




from django.db.models import Q  
from django.contrib.auth.models import User



class FriendListView(LoginRequiredMixin, ListView):
    template_name = 'gym_app/friend_list.html'
    context_object_name = 'friends'
    login_url = 'login'

    def get_queryset(self):
        profile = self.request.user.profile
        return profile.get_friends()

class AddFriendListView(LoginRequiredMixin, ListView):
    template_name = 'gym_app/add_friend_list.html'
    context_object_name = 'profiles'
    login_url = 'login'

    def get_queryset(self):
        current_user_profile = self.request.user.profile
        friends = current_user_profile.get_friends()
        excluded_profiles = [current_user_profile] + friends
        return Profile.objects.exclude(id__in=[p.id for p in excluded_profiles])

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    # check if they are friends.
    if not request.user.profile.is_friend(recipient.profile):
        return HttpResponseForbidden("You can only send messages to your friends.")
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.recipient = recipient
            new_message.save()
            messages.success(request, 'Message sent successfully.')
            return redirect('message_thread', user_id=recipient.id)
    else:
        form = MessageForm()
    return render(request, 'gym_app/send_message.html', {'form': form, 'recipient': recipient})

@login_required
def message_thread(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return HttpResponseForbidden("You cannot message yourself.")
    if not request.user.profile.is_friend(other_user.profile):
        return HttpResponseForbidden("You can only view conversations with your friends.")
    # having user info
    messages_qs = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('timestamp')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.recipient = other_user
            new_message.save()
            return redirect('message_thread', user_id=other_user.id)
    else:
        form = MessageForm()
    return render(request, 'gym_app/message_thread.html', {
        'chat_messages': messages_qs,  # change 'messages' to 'chat_messages'
        'other_user': other_user,
        'form': form,
    })

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You cannot delete this message.")
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully.')
        return redirect('message_thread', user_id=message.recipient.id)
    return render(request, 'gym_app/delete_message.html', {'message_obj': message})  

@login_required
def update_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You cannot edit this message.")
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message updated successfully.')
            return redirect('message_thread', user_id=message.recipient.id)
    else:
        form = MessageForm(instance=message)
    return render(request, 'gym_app/update_message.html', {'form': form, 'message_obj': message}) 

class ChatListView(LoginRequiredMixin, TemplateView):
    template_name = 'gym_app/chat_list.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # 获取所有好友
        profile = user.profile
        friends = profile.get_friends()
        context['friends'] = friends
        # having info about current user.
        messages_qs = Message.objects.filter(Q(sender=user) | Q(recipient=user))
        conversations = {}
        for message in messages_qs:
            if message.sender == user:
                other_user = message.recipient
            else:
                other_user = message.sender
            if other_user in conversations:
                if conversations[other_user] < message.timestamp:
                    conversations[other_user] = message.timestamp
            else:
                conversations[other_user] = message.timestamp
        # order
        conversations = sorted(conversations.items(), key=lambda x: x[1], reverse=True)
        context['conversations'] = [user for user, _ in conversations]
        return context