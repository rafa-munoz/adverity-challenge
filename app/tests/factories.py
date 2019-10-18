from datetime import datetime

from factory import SubFactory
from factory.django import DjangoModelFactory

from ..models import Campaign, DataSource, RowData


class CampaignF(DjangoModelFactory):
    class Meta:
        model = Campaign

    name = 'Campaign ńámë'


class DataSourceF(DjangoModelFactory):
    class Meta:
        model = DataSource

    name = 'DataSource ńámë'


class RowDataF(DjangoModelFactory):
    class Meta:
        model = RowData

    date = datetime.now().date()
    data_source = SubFactory(DataSourceF)
    campaign = SubFactory(CampaignF)
    clicks = 1
    impressions = 10
