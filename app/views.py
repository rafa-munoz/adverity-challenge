from plotly.offline import plot
import plotly.graph_objs as go

from django.db.models import Subquery, Sum
from django.db.models.query import QuerySet
from django.views.generic import TemplateView

from .models import RowData
from .storage import refresh_db


class IndexView(TemplateView):
    template_name = 'index.html'

    def _get_plot_div(self, qs: QuerySet):
        x_axis = []
        y_axis_clicks = []
        y_axis_impressions = []

        for obj in qs:
            x_axis.append(obj['date'])
            y_axis_clicks.append(obj['clicks_total'])
            y_axis_impressions.append(obj['impressions_total'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=y_axis_clicks,
            name='Clicks',
        ))
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=y_axis_impressions,
            name='Impressions',
        ))
        fig.update_layout(
            xaxis_tickformat='%d.%m.%y'
        )
        fig.update_layout(legend=dict(x=1, y=1.2))
        return plot(fig, output_type='div')

    @staticmethod
    def _get_filtered_data(filters) -> QuerySet:
        """
        Groups by latest date_created
        """
        newest = RowData.objects.order_by('-id')
        qs = RowData.objects.values(
            'date'
        ).filter(
            date_created=Subquery(newest.values('date_created')[:1]),
        ).annotate(
            clicks_total=Sum('clicks'),
            impressions_total=Sum('impressions'),
        ).order_by(
            'date'
        )

        if filters.get('data_sources'):
            qs = qs.filter(data_source__name__in=filters['data_sources'])

        if filters.get('campaigns'):
            qs = qs.filter(campaign__name__in=filters['campaigns'])

        return qs

    @staticmethod
    def _get_distinct(column_name: str):
        newest = RowData.objects.order_by('-id')
        qs = RowData.objects.values_list(
            column_name, flat=True,
        ).filter(
            date_created=Subquery(newest.values('date_created')[:1]),
        ).distinct(
            column_name,
        )
        return qs

    def get_context_data(self, **kwargs):
        refresh_db()

        filters = {}
        selected_data_sources = self.request.GET.getlist('data-sources')
        if selected_data_sources:
            filters['data_sources'] = selected_data_sources

        selected_campaigns = self.request.GET.getlist('campaigns')
        if selected_campaigns:
            filters['campaigns'] = selected_campaigns

        qs = self._get_filtered_data(filters)
        plot_div = self._get_plot_div(qs)

        context = super().get_context_data(**kwargs)
        context['plot_div'] = plot_div
        context['data_sources'] = self._get_distinct('data_source__name')
        context['campaigns'] = self._get_distinct('campaign__name')
        context['selected_data_sources'] = selected_data_sources
        context['selected_campaigns'] = selected_campaigns
        return context
