from datetime import date
from io import StringIO

from django.test import TestCase

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

    def test_extract(self):
        """
        Ensures that the data extraction works.
        """
        self.csv_data.process()

        self.assertListEqual(
            self.csv_data.cleaned_data,
            [
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
                    'date': date(2019, 1, 1),
                    'data_source': 'Google Adwords',
                    'campaign': 'Like Ads',
                    'clicks': 7,
                    'impressions': 444,
                },
                {
                    'date': date(2019, 1, 1),
                    'data_source': 'Google Adwords',
                    'campaign': 'GDN Prio 1 Offer',
                    'clicks': 16,
                    'impressions': 12535,
                },
                {
                    'date': date(2019, 1, 1),
                    'data_source': 'Google Adwords',
                    'campaign': 'GDN Prio 2 Offer',
                    'clicks': 93,
                    'impressions': 18866,
                },
                {
                    'date': date(2019, 1, 2),
                    'data_source': 'Google Analytics',
                    'campaign': 'Like Ads',
                    'clicks': 7,
                    'impressions': 51,
                },
                {
                    'date': date(2019, 1, 2),
                    'data_source': 'Google Analytics',
                    'campaign': 'POL Desktop',
                    'clicks': 5,
                    'impressions': 1103,
                },
            ]
        )


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
