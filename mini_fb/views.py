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
    ImageFormSet
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
        """从查询参数获取 Profile 的 pk 并返回对应的 Profile 对象。"""
        pk = self.request.GET.get('pk')
        if not pk:
            raise Http404("Profile pk is required.")
        profile = get_object_or_404(Profile, pk=pk, user=self.request.user)
        return profile

    def test_func(self):
        """确保用户正在更新自己的 Profile。"""
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        """成功更新后重定向到 Profile 页面。"""
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(LoginRequiredMixin, View):
    """允许用户为其 Profile 创建新的 StatusMessage，包括上传照片。"""

    def get(self, request, *args, **kwargs):
        """显示创建 StatusMessage 的表单和 ImageFormSet。"""
        pk = request.GET.get('pk')
        if not pk:
            return redirect('create_profile')
        profile = get_object_or_404(Profile, pk=pk, user=request.user)
        form = CreateStatusMessageForm()
        formset = ImageFormSet()
        return render(request, 'mini_fb/create_status_form.html', {
            'form': form,
            'formset': formset,
            'profile': profile
        })
    
    def post(self, request, *args, **kwargs):
        """处理提交的 StatusMessage 表单和 ImageFormSet。"""
        pk = request.GET.get('pk')
        if not pk:
            return redirect('create_profile')
        profile = get_object_or_404(Profile, pk=pk, user=request.user)
        form = CreateStatusMessageForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            status = form.save(commit=False)
            status.profile = profile
            status.save()
            # 处理图片上传
            images = formset.save(commit=False)
            for image in images:
                image.status_message = status
                image.save()
            # 处理删除的图片
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('show_profile', pk=profile.pk)
        return render(request, 'mini_fb/create_status_form.html', {
            'form': form,
            'formset': formset,
            'profile': profile
        })

class UpdateStatusMessageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """允许用户更新自己的 StatusMessage，包括添加或删除照片。"""
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status'

    def get_object(self, queryset=None):
        """获取特定的 StatusMessage 对象。"""
        status = get_object_or_404(StatusMessage, pk=self.kwargs['pk'], profile__user=self.request.user)
        return status

    def get_context_data(self, **kwargs):
        """将 ImageFormSet 添加到上下文。"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = ImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        """处理表单和 formset 的有效数据。"""
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            # 处理删除的图片
            formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('show_profile', pk=self.object.profile.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

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
        other_profile = get_object_or_404(Profile, pk=other_pk, user__is_active=True)
        if other_profile == profile:
            # 防止添加自己为好友
            return redirect('show_profile', pk=profile.pk)
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)

class ShowFriendSuggestionsView(LoginRequiredMixin, TemplateView):
    """显示当前用户 Profile 的好友建议。"""
    template_name = 'mini_fb/friend_suggestions.html'

    def get_context_data(self, **kwargs):
        """将好友建议添加到上下文。"""
        context = super().get_context_data(**kwargs)
        pk = self.request.GET.get('pk')
        print(f"ShowFriendSuggestionsView: Received pk={pk}")  # 调试语句
        if not pk:
            context['profile'] = None
            context['suggested_friends'] = []
            return context
        profile = get_object_or_404(Profile, pk=pk, user=self.request.user)
        context['profile'] = profile
        context['suggested_friends'] = profile.get_friend_suggestions()
        return context

class ShowNewsFeedView(LoginRequiredMixin, TemplateView):
    """显示当前用户 Profile 的新闻源。"""
    template_name = 'mini_fb/news_feed.html'

    def get_context_data(self, **kwargs):
        """将新闻源添加到上下文。"""
        context = super().get_context_data(**kwargs)
        pk = self.request.GET.get('pk')
        print(f"ShowNewsFeedView: Received pk={pk}")  # 调试语句
        if not pk:
            context['profile'] = None
            context['news_feed'] = []
            return context
        profile = get_object_or_404(Profile, pk=pk, user=self.request.user)
        context['profile'] = profile
        context['news_feed'] = profile.get_news_feed()
        return context
