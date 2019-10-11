from collections import OrderedDict
import csv
import re
from typing import Dict, Tuple
from urllib import request

from io import StringIO


def get_data(url: str) -> StringIO:
    stream = request.urlopen(url)
    content = stream.read().decode('utf-8')
    content = StringIO(content)
    return content


class CSVData:
    def __init__(self, content: StringIO):
        self._content = content
        self._timeline: OrderedDict = OrderedDict()
        self._data_sources: Tuple = tuple()
        self._campaigns: Tuple = tuple()

    @property
    def timeline(self) -> Dict[str, Dict[str, int]]:
        return self._timeline

    @property
    def data_sources(self) -> tuple:
        return self._data_sources

    @property
    def campaigns(self) -> tuple:
        return self._campaigns

    def process(self, filters: Dict[str, list] = None) -> None:
        """
        Given a CSV content, processes the data and .

        :param filters: Dict of filters. Possible keys:
                        'data_sources', 'campaigns'.
        """
        csv_reader = csv.DictReader(self._content)

        self._timeline.clear()
        data_sources = set()
        campaigns = set()

        for row in csv_reader:
            if not self._is_valid_data(row):
                continue

            date = row['Date']
            data_source = row['Datasource']
            campaign = row['Campaign']
            clicks = int(row['Clicks'])
            impressions = int(row['Impressions'])

            data_sources.add(data_source)
            campaigns.add(campaign)

            # Apply filters
            if filters:
                if isinstance(filters.get('data_sources'), list):
                    if data_source not in filters['data_sources']:
                        continue

                if isinstance(filters.get('campaigns'), list):
                    if campaign not in filters['campaigns']:
                        continue

            if date not in self.timeline:
                self.timeline[date] = {
                    'clicks': clicks,
                    'impressions': impressions,
                }
            else:
                self.timeline[date]['clicks'] += clicks
                self.timeline[date]['impressions'] += impressions

        self._data_sources = tuple(sorted(data_sources))
        self._campaigns = tuple(sorted(campaigns))

    @staticmethod
    def _is_valid_data(row: dict) -> bool:
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', row['Date']):
            return False

        if not isinstance(row['Datasource'], str) or not row['Datasource']:
            return False

        if not isinstance(row['Campaign'], str) or not row['Campaign']:
            return False

        try:
            int(row['Clicks'])
            int(row['Impressions'])
        except ValueError:
            return False

        return True
