from datetime import datetime

from django.test import TestCase

from ..views import IndexView
from .factories import RowDataF


class TestIndexView(TestCase):
    def test_get_filtered_data_just_for_latest(self):
        """
        Ensures that only creation dates of the latest created RowData registry
        are returned.
        """
        row_data = RowDataF()
        row_data.date_created = datetime(2018, 12, 30)
        row_data.save()

        RowDataF.create_batch(2)

        qs = IndexView._get_filtered_data({})

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0]['date'], datetime(2019, 10, 18).date())
        self.assertEqual(qs[0]['clicks_total'], 2)
        self.assertEqual(qs[0]['impressions_total'], 20)

    def test_get_filtered_data_single_data_source(self):
        """
        Ensures data gets filtered by a single data source.
        """
        RowDataF.create_batch(2)
        qs = IndexView._get_filtered_data({
            'data_sources': ['Cannot be found'],
        })
        self.assertEqual(qs.count(), 0)

        qs = IndexView._get_filtered_data({
            'data_sources': ['DataSource ńámë'],
        })
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0]['date'], datetime(2019, 10, 18).date())
        self.assertEqual(qs[0]['clicks_total'], 2)
        self.assertEqual(qs[0]['impressions_total'], 20)

    def test_get_filtered_data_multiple_data_sources(self):
        """
        Ensures data gets filtered by a many data sources.
        """
        RowDataF.create_batch(2)
        RowDataF(data_source__name='Extra Source', date=datetime(2019, 5, 10))
        qs = IndexView._get_filtered_data({
            'data_sources': ['DataSource ńámë', 'Extra Source'],
        })
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs[0]['date'], datetime(2019, 5, 10).date())
        self.assertEqual(qs[0]['clicks_total'], 1)
        self.assertEqual(qs[0]['impressions_total'], 10)
        self.assertEqual(qs[1]['date'], datetime(2019, 10, 18).date())
        self.assertEqual(qs[1]['clicks_total'], 2)
        self.assertEqual(qs[1]['impressions_total'], 20)

    def test_get_filtered_data_single_campaign(self):
        """
        Ensures data gets filtered by a single campaign.
        """
        RowDataF.create_batch(2)
        qs = IndexView._get_filtered_data({
            'campaigns': ['Cannot be found'],
        })
        self.assertEqual(qs.count(), 0)

        qs = IndexView._get_filtered_data({
            'campaigns': ['Campaign ńámë'],
        })
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0]['date'], datetime(2019, 10, 18).date())
        self.assertEqual(qs[0]['clicks_total'], 2)
        self.assertEqual(qs[0]['impressions_total'], 20)

    def test_get_filtered_data_multiple_campaigns(self):
        """
        Ensures data gets filtered by multiple campaigns.
        """
        RowDataF.create_batch(2)
        qs = IndexView._get_filtered_data({
            'data_sources': ['Cannot be found'],
        })
        self.assertEqual(qs.count(), 0)

        qs = IndexView._get_filtered_data({
            'campaigns': ['Campaign ńámë'],
        })
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0]['date'], datetime(2019, 10, 18).date())
        self.assertEqual(qs[0]['clicks_total'], 2)
        self.assertEqual(qs[0]['impressions_total'], 20)


class TestGetCampaignsDataSources(TestCase):
    def test_get_distinct(self):
        RowDataF()

        result = IndexView._get_distinct('campaign__name')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], 'Campaign ńámë')

        result = IndexView._get_distinct('data_source__name')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], 'DataSource ńámë')
