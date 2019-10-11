from collections import OrderedDict
from io import StringIO
from unittest import TestCase

from ..extraction import CSVData


class TestCSVData(TestCase):
    def setUp(self) -> None:
        content = StringIO("""\
Date,Datasource,Campaign,Clicks,Impressions
01.01.2019,Facebook Ads,Like Ads,274,1979
01.01.2019,Facebook Ads,Offer Campaigns,10245,764627
01.01.2019,Google Adwords,Like Ads,7,444
01.01.2019,Google Adwords,GDN Prio 1 Offer,16,12535
01.01.2019,Google Adwords,GDN Prio 2 Offer,93,18866
02.01.2019,Google Analytics,Like Ads,7,51
02.01.2019,Google Analytics,POL Desktop,5,1103
        """)
        self.csv_data = CSVData(content)

    def test_data_sources(self):
        self.csv_data.process()
        self.assertEqual(
            self.csv_data.data_sources,
            ('Facebook Ads', 'Google Adwords', 'Google Analytics'),
        )

    def test_campaigns(self):
        self.csv_data.process()
        self.assertEqual(
            self.csv_data.campaigns,
            ('GDN Prio 1 Offer', 'GDN Prio 2 Offer', 'Like Ads',
             'Offer Campaigns', 'POL Desktop'),
        )

    def test_extract_simple(self):
        """
        Ensures that the most simple form of data extraction works. No filter
        is applied.
        """
        self.csv_data.process()
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019', '02.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 10635)
        self.assertEqual(timeline['01.01.2019']['impressions'], 798451)
        self.assertEqual(timeline['02.01.2019']['clicks'], 12)
        self.assertEqual(timeline['02.01.2019']['impressions'], 1154)

    def test_extract_filter_by_single_datasource(self):
        """
        Ensures that filtering by a single datasource works as it should.
        """
        self.csv_data.process({'data_sources': ['Facebook Ads']})
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 10519)
        self.assertEqual(timeline['01.01.2019']['impressions'], 766606)

    def test_extract_filter_by_multiple_data_sources(self):
        """
        Ensures that filtering by multiple data_sources works as it should.
        """
        self.csv_data.process(
            {'data_sources': ['Facebook Ads', 'Google Analytics']}
        )
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019', '02.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 10519)
        self.assertEqual(timeline['01.01.2019']['impressions'], 766606)
        self.assertEqual(timeline['02.01.2019']['clicks'], 12)
        self.assertEqual(timeline['02.01.2019']['impressions'], 1154)

    def test_extract_filter_by_single_campaign(self):
        """
        Ensures that filtering by a single campaign works as it should.
        """
        self.csv_data.process({'campaigns': ['Like Ads']})
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019', '02.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 281)
        self.assertEqual(timeline['01.01.2019']['impressions'], 2423)
        self.assertEqual(timeline['02.01.2019']['clicks'], 7)
        self.assertEqual(timeline['02.01.2019']['impressions'], 51)

    def test_extract_filter_by_multiple_campaigns(self):
        """
        Ensures that filtering by a multiple campaigns works as it should.
        """
        self.csv_data.process({'campaigns': ['Like Ads', 'POL Desktop']})
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019', '02.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 281)
        self.assertEqual(timeline['01.01.2019']['impressions'], 2423)
        self.assertEqual(timeline['02.01.2019']['clicks'], 7 + 5)
        self.assertEqual(timeline['02.01.2019']['impressions'], 51 + 1103)

    def test_extract_filter_by_single_datasource_and_campaign(self):
        """
        Ensures that filtering by both datasource and campaign works as it
        should.
        """
        self.csv_data.process({
            'data_sources': ['Google Analytics'],
            'campaigns': ['Like Ads']
        })
        timeline = self.csv_data.timeline

        self.assertEqual(
            [t for t in timeline.keys()],
            ['02.01.2019'],
        )
        self.assertEqual(timeline['02.01.2019']['clicks'], 7)
        self.assertEqual(timeline['02.01.2019']['impressions'], 51)

        self.csv_data.process({
            'data_sources': ['Facebook Ads'],
            'campaigns': ['POL Desktop']
        })
        timeline = self.csv_data.timeline
        self.assertEqual(timeline, OrderedDict())

    def test_extract_filter_by_multiple_data_sources_and_campaigns(self):
        self.csv_data.process({
            'data_sources': ['Facebook Ads', 'Google Analytics'],
            'campaigns': ['Like Ads', 'Offer Campaigns'],
        })
        timeline = self.csv_data.timeline
        self.assertEqual(
            [t for t in timeline.keys()],
            ['01.01.2019', '02.01.2019'],
        )
        self.assertEqual(timeline['01.01.2019']['clicks'], 10519)
        self.assertEqual(timeline['01.01.2019']['impressions'], 766606)
        self.assertEqual(timeline['02.01.2019']['clicks'], 7)
        self.assertEqual(timeline['02.01.2019']['impressions'], 51)


class TestCSVDataIsValidData(TestCase):
    def setUp(self) -> None:
        self.row = {
            'Date': '31.10.2019',
            'Datasource': 'Data source',
            'Campaign': 'Campaign',
            'Clicks': '100',
            'Impressions': '2000',
        }

    def test_validates_successfully(self):
        self.assertTrue(CSVData._is_valid_data(self.row))

    def test_wrong_date_doesnt_validate(self):
        self.row['Date'] = ''
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Date'] = '1.10.2019'
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Date'] = '31.1.2019'
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Date'] = '31.01.19'
        self.assertFalse(CSVData._is_valid_data(self.row))

    def test_wrong_datasource_doesnt_validate(self):
        self.row['Datasource'] = None
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Datasource'] = ''
        self.assertFalse(CSVData._is_valid_data(self.row))

    def test_wrong_campaign_doesnt_validate(self):
        self.row['Campaign'] = None
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Campaign'] = ''
        self.assertFalse(CSVData._is_valid_data(self.row))

    def test_wrong_clicks_doesnt_validate(self):
        self.row['Clicks'] = ''
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Clicks'] = '1A'
        self.assertFalse(CSVData._is_valid_data(self.row))

    def test_wrong_impressions_doesnt_validate(self):
        self.row['Impressions'] = ''
        self.assertFalse(CSVData._is_valid_data(self.row))

        self.row['Impressions'] = '1A'
        self.assertFalse(CSVData._is_valid_data(self.row))
