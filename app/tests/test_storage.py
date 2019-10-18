import copy
from datetime import date, datetime, timedelta
from unittest import mock

from django.conf import settings
from django.test import TestCase

from ..extraction import CSVData
from ..models import Campaign, DataSource, RowData
from ..storage import refresh_db, _store_data
from .factories import RowDataF


class TestRefreshDB(TestCase):
    @mock.patch('app.storage._store_data')
    def test_empty_db(self, mock_store_data):
        """
        Ensures that in case of an empty DB, the data storage process gets
        triggered.
        """
        refresh_db()
        mock_store_data.assert_called_once_with()

    @mock.patch('app.storage._store_data')
    def test_up_to_date_data(self, mock_store_data):
        """
        Ensures that in case the database DB contains new data, the data
        storage process does not gets triggered.
        """
        RowDataF()
        refresh_db()
        self.assertFalse(mock_store_data.called)

    @mock.patch('app.storage._store_data')
    def test_old_data(self, mock_store_data):
        """
        Ensures that in case the database DB contains old data, the data
        storage process gets triggered.
        """
        row_data = RowDataF()
        date_expired = (
            datetime.utcnow() -
            timedelta(days=settings.DATA_REFRESH_DAYS + 1)
        )
        row_data.date_created = date_expired
        row_data.save()
        refresh_db()
        mock_store_data.assert_called_once_with()


class TestStoreData(TestCase):
    @mock.patch('app.storage._get_data')
    @mock.patch('app.storage.CSVData')
    def test_store_date(self, mock_csv_data, _mock_get_data):
        mock_obj = mock.MagicMock(spec=CSVData)
        mock_obj.campaigns = ('Like Ads', 'Offer Campaigns')
        mock_obj.data_sources = ('Facebook Ads', 'Google Adwords')
        mock_obj.cleaned_data = [
            {
                'date': date(2019, 1, 1),
                'data_source': 'Facebook Ads',
                'campaign': 'Like Ads',
                'clicks': 274,
                'impressions': 1979,
            },
            {
                'date': date(2019, 1, 1),
                'data_source': 'Facebook Ads',
                'campaign': 'Offer Campaigns',
                'clicks': 10245,
                'impressions': 764627,
            },
            {
                'date': date(2019, 12, 31),
                'data_source': 'Google Adwords',
                'campaign': 'Like Ads',
                'clicks': 7,
                'impressions': 444,
            },
        ]
        cleaned_data = copy.deepcopy(mock_obj.cleaned_data)
        mock_csv_data.return_value = mock_obj
        _store_data()

        self.assertEqual(Campaign.objects.all().count(), 2)
        self.assertEqual(DataSource.objects.all().count(), 2)
        self.assertEqual(RowData.objects.all().count(), 3)
        for i, row_data in enumerate(RowData.objects.all()):
            self.assertEqual(row_data.date, cleaned_data[i]['date'])
            self.assertEqual(
                row_data.data_source.name, cleaned_data[i]['data_source']
            )
            self.assertEqual(
                row_data.campaign.name, cleaned_data[i]['campaign']
            )
            self.assertEqual(row_data.clicks, cleaned_data[i]['clicks'])
            self.assertEqual(
                row_data.impressions, cleaned_data[i]['impressions']
            )
