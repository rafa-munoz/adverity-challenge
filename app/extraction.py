import csv
from datetime import datetime
from io import StringIO
import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


class CSVData:
    def __init__(self, content: StringIO):
        self._content = content
        self._data: List[dict] = []
        self._data_sources: Tuple = tuple()
        self._campaigns: Tuple = tuple()

    @property
    def cleaned_data(self) -> List[dict]:
        return self._data

    @property
    def data_sources(self) -> tuple:
        return self._data_sources

    @property
    def campaigns(self) -> tuple:
        return self._campaigns

    def process(self):
        """
        Given a CSV content, it processes the data. The processed and validated
        data can be retrieved using the class' public properties.
        """
        csv_reader = csv.DictReader(self._content)

        self._data.clear()
        data_sources = set()
        campaigns = set()

        for row in csv_reader:
            if not self._is_valid_data(row):
                logger.info(f'Invalid data. Skipped row: {row}')
                continue

            data_source: str = row['Datasource']
            campaign: str = row['Campaign']
            data_sources.add(data_source)
            campaigns.add(campaign)

            self._data.append({
                'date': datetime.strptime(row['Date'], '%d.%m.%Y').date(),
                'data_source': data_source,
                'campaign': campaign,
                'clicks': int(row['Clicks']),
                'impressions': int(row['Impressions']),
            })

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
