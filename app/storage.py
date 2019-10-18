from datetime import datetime, timedelta
from io import StringIO
from urllib import request

from django.conf import settings
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware

from .extraction import CSVData
from .models import Campaign, DataSource, RowData


def refresh_db() -> None:
    """
    Checks against the database if the data is up-to-date according to
    DATA_REFRESH_DAYS value. In case it is not, then it stores the new data.
    """
    time_threshold = make_aware(
        datetime.utcnow() - timedelta(days=settings.DATA_REFRESH_DAYS)
    ).date()
    try:
        date_created_latest = RowData.objects.values_list(
            'date_created', flat=True).latest('id')
    except RowData.DoesNotExist:
        date_created_latest = None

    if date_created_latest is None or date_created_latest <= time_threshold:
        _store_data()


def _get_data(url: str) -> StringIO:
    stream = request.urlopen(url)
    content = stream.read().decode('utf-8')
    content = StringIO(content)
    return content


def _store_data() -> None:
    """
    Retrieves the CSV data and stores it in the database.
    """
    content = _get_data(settings.ENDPOINT_URL)
    csv_data = CSVData(content)
    csv_data.process()

    # Store data sources
    data_sources = {}
    for data_source_name in csv_data.data_sources:
        data_source, _ = DataSource.objects.get_or_create(
            name=data_source_name)
        data_sources[data_source_name] = data_source.id

    # Store campaigns
    campaigns = {}
    for campaign_name in csv_data.campaigns:
        campaign, _ = Campaign.objects.get_or_create(
            name=campaign_name)
        campaigns[campaign_name] = campaign.id

    # Store data rows
    row_data_list = []
    for data in csv_data.cleaned_data:
        data['data_source_id'] = data_sources[data['data_source']]
        del data['data_source']
        data['campaign_id'] = campaigns[data['campaign']]
        del data['campaign']
        row_data_list.append(RowData(**data))

    # To avoid race conditions of two requests entering at the same time in
    # this statement, we set a unique_together at database level and we
    # manage the integrity error in case it arises.
    try:
        RowData.objects.bulk_create(row_data_list)
    except IntegrityError:
        pass
