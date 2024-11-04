# mini_fb/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.http import Http404
from .models import Profile, StatusMessage, Image, Friend
from .forms import (
    CreateProfileForm, 
    CreateStatusMessageForm, 
    UpdateProfileForm, 
    UpdateStatusMessageForm,
    UserRegistrationForm,
)

class ShowAllProfilesView(ListView):
    """显示所有 Profiles 的列表。"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    """显示单个 Profile 的详细信息。"""
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """根据 URL 中的 pk 获取 Profile。"""
        return get_object_or_404(Profile, pk=self.kwargs['pk'])

class CreateProfileView(FormView):
    """处理用户注册和 Profile 创建。"""
    template_name = 'mini_fb/create_profile_form.html'
    form_class = UserRegistrationForm

    def get_context_data(self, **kwargs):
        """将 CreateProfileForm 添加到上下文。"""
        context = super().get_context_data(**kwargs)
        context['profile_form'] = CreateProfileForm(self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        """处理 UserRegistrationForm 和 CreateProfileForm。"""
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            # 如果用户已认证且已有 Profiles，阻止创建新的 Profile
            if self.request.user.is_authenticated and self.request.user.profiles.exists():
                form.add_error(None, "您已经拥有一个或多个 Profiles。")
                return self.form_invalid(form)
            
            # 创建 User
            user = form.save()
            # 创建 Profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # 登录用户
            login(self.request, user)
            self.profile = profile  # 保存 Profile 以获取成功 URL
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        """重定向到新创建的 Profile 页面。"""
        return reverse('show_profile', kwargs={'pk': self.profile.pk})

class UpdateProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """允许用户更新自己的 Profile。"""
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """获取当前用户的第一个 Profile。"""
        profile = self.request.user.profiles.first()
        if not profile:
            raise Http404("未找到与该用户关联的 Profile。")
        return profile

    def test_func(self):
        """确保用户正在更新自己的 Profile。"""
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        """成功更新后重定向到 Profile 页面。"""
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(LoginRequiredMixin, View):
    """允许用户为其 Profile 创建新的 StatusMessage。"""

    def get(self, request, *args, **kwargs):
        """显示创建 StatusMessage 的表单。"""
        profile = request.user.profiles.first()
        if not profile:
            return redirect('create_profile')
        form = CreateStatusMessageForm()
        return render(request, 'mini_fb/create_status_form.html', {'form': form, 'profile': profile})
    
    def post(self, request, *args, **kwargs):
        """处理提交的 StatusMessage 表单。"""
        profile = request.user.profiles.first()
        if not profile:
            return redirect('create_profile')
        form = CreateStatusMessageForm(request.POST, request.FILES)
        if form.is_valid():
            status = form.save(commit=False)
            status.profile = profile
            status.save()
            # 处理图片上传
            files = request.FILES.getlist('files')
            for f in files:
                Image.objects.create(status_message=status, image_file=f)
            return redirect('show_profile', pk=profile.pk)
        return render(request, 'mini_fb/create_status_form.html', {'form': form, 'profile': profile})

class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """允许用户更新自己的 StatusMessage。"""
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status'

    def test_func(self):
        """确保用户拥有该 StatusMessage。"""
        status = self.get_object()
        return self.request.user == status.profile.user

    def get_success_url(self):
        """成功更新后重定向到 Profile 页面。"""
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})

class DeleteStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """允许用户删除自己的 StatusMessage。"""
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status'

    def test_func(self):
        """确保用户拥有该 StatusMessage。"""
        status = self.get_object()
        return self.request.user == status.profile.user

    def get_success_url(self):
        """成功删除后重定向到 Profile 页面。"""
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})

class CreateFriendView(LoginRequiredMixin, UserPassesTestMixin, View):
    """处理将一个 Profile 添加为好友。"""

    def test_func(self):
        """确保用户拥有至少一个 Profile。"""
        return self.request.user.profiles.exists()

    def post(self, request, other_pk, *args, **kwargs):
        """处理添加好友的逻辑。"""
        profile = request.user.profiles.first()
        if not profile:
            return redirect('create_profile')
        other_profile = get_object_or_404(Profile, pk=other_pk)
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)

class ShowFriendSuggestionsView(LoginRequiredMixin, TemplateView):
    """显示当前用户 Profile 的好友建议。"""
    template_name = 'mini_fb/friend_suggestions.html'

    def get_context_data(self, **kwargs):
        """将好友建议添加到上下文。"""
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profiles.first()
        if profile:
            context['profile'] = profile
            context['suggested_friends'] = profile.get_friend_suggestions()
        else:
            context['profile'] = None
            context['suggested_friends'] = []
        return context

class ShowNewsFeedView(LoginRequiredMixin, TemplateView):
    """显示当前用户 Profile 的新闻源。"""
    template_name = 'mini_fb/news_feed.html'

    def get_context_data(self, **kwargs):
        """将新闻源添加到上下文。"""
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profiles.first()
        if profile:
            context['profile'] = profile
            context['news_feed'] = profile.get_news_feed()
        else:
            context['profile'] = None
            context['news_feed'] = []
        return context
