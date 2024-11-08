
# Create your views here.
# voter_analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Voter
from .forms import FilterForm
import datetime

class VotersListView(ListView):
    """
    View to display a list of Voter records with pagination and filtering.
    """
    model = Voter
    template_name = 'voter_analytics/voters_list.html'
    context_object_name = 'results'
    paginate_by = 100  # 每页显示100条记录
    
    def get_queryset(self):
        """
        Override the default queryset to apply filters based on GET parameters.
        """
        qs = super().get_queryset().order_by('last_name', 'first_name')
        
        # 获取过滤参数
        party = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        elections = self.request.GET.getlist('elections')  # 获取多个选项
        
        # 过滤逻辑
        if party and party != 'All':
            qs = qs.filter(party_affiliation=party)
        
        if min_dob:
            try:
                min_dob_year = int(min_dob)
                qs = qs.filter(date_of_birth__year__gte=min_dob_year)
            except ValueError:
                pass  # 忽略格式错误
        
        if max_dob:
            try:
                max_dob_year = int(max_dob)
                qs = qs.filter(date_of_birth__year__lte=max_dob_year)
            except ValueError:
                pass  # 忽略格式错误
        
        if voter_score and voter_score != 'All':
            qs = qs.filter(voter_score=voter_score)
        
        if elections:
            for election in elections:
                if election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
                    filter_kwargs = {election: True}
                    qs = qs.filter(**filter_kwargs)
        
        return qs
    
    def get_context_data(self, **kwargs):
        """
        Add the filter form to the context.
        """
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FilterForm(self.request.GET)
        return context
    
class VoterDetailView(DetailView):
    """
    View to display details of a single Voter.
    """
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'r'
