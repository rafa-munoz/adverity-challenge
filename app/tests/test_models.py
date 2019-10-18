from datetime import date, datetime

from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import Campaign, DataSource, RowData
from .factories import CampaignF, DataSourceF, RowDataF


class TestCampaign(TestCase):
    def test_save(self):
        CampaignF()
        campaign = Campaign.objects.all().first()
        self.assertTrue(isinstance(campaign.date_created, datetime))
        self.assertEqual(campaign.name, 'Campaign ńámë')


class TestDataSource(TestCase):
    def test_save(self):
        DataSourceF()
        data_source = DataSource.objects.all().first()
        self.assertTrue(isinstance(data_source.date_created, datetime))
        self.assertEqual(data_source.name, 'DataSource ńámë')


class TestRowData(TestCase):
    def setUp(self):
        self.data_source = DataSourceF()
        self.campaign = CampaignF()
        self.row_data = RowDataF.build(
            data_source=self.data_source, campaign=self.campaign
        )

    def test_save(self):
        self.row_data.save()
        row_data = RowData.objects.all().first()
        self.assertTrue(isinstance(row_data.date_created, date))
        self.assertTrue(isinstance(row_data.date, date))
        self.assertEqual(row_data.data_source, self.data_source)
        self.assertEqual(row_data.campaign, self.campaign)

    def test_bulk_save_unique_constraints(self):
        """
        Ensures that creating objects in bulk cannot be done twice for the same
        data. It will avoid race conditions.
        """

        RowData.objects.bulk_create([self.row_data])

        with self.assertRaises(IntegrityError):
            RowData.objects.bulk_create([self.row_data])
