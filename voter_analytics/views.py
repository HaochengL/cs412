# voter_analytics/views.py

from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Voter
from .forms import FilterForm
import datetime
import plotly
import plotly.graph_objs as go
from collections import defaultdict  # Needed for Graph 2

class VotersListView(ListView):
    """
    View to display a list of Voter records with pagination and filtering.
    """
    model = Voter
    template_name = 'voter_analytics/voters_list.html'
    context_object_name = 'results'
    paginate_by = 100  # Display 100 records per page

    def get_queryset(self):
        """
        Override the default queryset to apply filters based on GET parameters.
        """
        qs = super().get_queryset().order_by('last_name', 'first_name')

        # Get filter parameters
        party = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        elections = self.request.GET.getlist('elections')  # Get multiple options

        # Filtering logic
        if party and party != 'All':
            qs = qs.filter(party_affiliation__iexact=party.strip())

        if min_dob:
            try:
                qs = qs.filter(date_of_birth__year__gte=int(min_dob))
            except ValueError:
                pass  # Ignore format errors

        if max_dob:
            try:
                qs = qs.filter(date_of_birth__year__lte=int(max_dob))
            except ValueError:
                pass  # Ignore format errors

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

class GraphsView(TemplateView):
    """
    View to display graphs of Voter data with filtering.
    """
    template_name = 'voter_analytics/graphs.html'

    def get_context_data(self, **kwargs):
        """
        Add graphs and filter form to the context.
        """
        context = super().get_context_data(**kwargs)
        form = FilterForm(self.request.GET)
        context['filter_form'] = form

        # Get filter parameters
        qs = Voter.objects.all()
        party = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        elections = self.request.GET.getlist('elections')

        # Filtering logic
        if party and party != 'All':
            qs = qs.filter(party_affiliation__iexact=party.strip())

        if min_dob:
            try:
                qs = qs.filter(date_of_birth__year__gte=int(min_dob))
            except ValueError:
                pass  # Ignore format errors

        if max_dob:
            try:
                qs = qs.filter(date_of_birth__year__lte=int(max_dob))
            except ValueError:
                pass  # Ignore format errors

        if voter_score and voter_score != 'All':
            qs = qs.filter(voter_score=voter_score)

        if elections:
            for election in elections:
                if election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
                    filter_kwargs = {election: True}
                    qs = qs.filter(**filter_kwargs)

        # Graph 1: Distribution of Voters by Year of Birth (Histogram)
        birth_years = qs.values_list('date_of_birth__year', flat=True)
        birth_year_counts = {}
        for year in birth_years:
            birth_year_counts[year] = birth_year_counts.get(year, 0) + 1
        sorted_years = sorted(birth_year_counts.keys())
        sorted_counts = [birth_year_counts[year] for year in sorted_years]

        hist_trace = go.Bar(x=sorted_years, y=sorted_counts)
        hist_layout = go.Layout(
            title='Distribution of Voters by Year of Birth',
            xaxis=dict(title='Year of Birth'),
            yaxis=dict(title='Number of Voters')
        )
        hist_fig = go.Figure(data=[hist_trace], layout=hist_layout)
        graph_div_birth = plotly.offline.plot(hist_fig, auto_open=False, output_type='div')
        context['graph_div_birth'] = graph_div_birth

        # Graph 2: Distribution of Voters by Party Affiliation (Pie Chart)
        party_affiliations = qs.values_list('party_affiliation', flat=True)
        party_counts = defaultdict(int)
        for party_affiliation in party_affiliations:
            party = party_affiliation.strip()
            party_counts[party] += 1

        total_voters = sum(party_counts.values())
        threshold = 0.02  # Parties with less than 2% will be grouped into 'Other'
        other_count = 0
        filtered_party_counts = {}

        for party, count in party_counts.items():
            percentage = count / total_voters
            if percentage < threshold:
                other_count += count
            else:
                filtered_party_counts[party] = count

        if other_count > 0:
            filtered_party_counts['其他'] = other_count  # 合并为“其他”

        # Sorting labels and values
        sorted_items = sorted(filtered_party_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_items:
            labels, values = zip(*sorted_items)
        else:
            labels, values = [], []

        pie_trace = go.Pie(
            labels=labels,
            values=values,
            hoverinfo='label+percent+value',
            textinfo='percent+label',
            insidetextorientation='radial'
        )
        pie_layout = go.Layout(
            title='Distribution of Voters by Party Affiliation',
            width=800,
            height=600,
            legend=dict(
                x=1,
                y=0.5,
                xanchor='left',
                yanchor='middle'
            ),
            margin=dict(l=50, r=150, t=50, b=50),
        )
        pie_fig = go.Figure(data=[pie_trace], layout=pie_layout)
        graph_div_party = plotly.offline.plot(pie_fig, auto_open=False, output_type='div')
        context['graph_div_party'] = graph_div_party

        # Graph 3: Participation in Past Elections (Bar Chart)
        elections_list = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_counts = {}
        for election in elections_list:
            count = qs.filter(**{election: True}).count()
            election_counts[election] = count
        bar_x = [
            '2020 State Election' if e == 'v20state' else
            '2021 Town Election' if e == 'v21town' else
            '2021 Primary Election' if e == 'v21primary' else
            '2022 General Election' if e == 'v22general' else
            '2023 Town Election' for e in elections_list
        ]
        bar_y = [election_counts[election] for election in elections_list]

        bar_trace = go.Bar(x=bar_x, y=bar_y)
        bar_layout = go.Layout(
            title='Participation in Past Elections',
            xaxis=dict(title='Election'),
            yaxis=dict(title='Number of Voters')
        )
        bar_fig = go.Figure(data=[bar_trace], layout=bar_layout)
        graph_div_elections = plotly.offline.plot(bar_fig, auto_open=False, output_type='div')
        context['graph_div_elections'] = graph_div_elections

        return context
