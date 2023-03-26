import logging
import pandas as pd
import xml.etree.ElementTree as ETree

from typing import Any
from decimal import Decimal, InvalidOperation, ROUND_DOWN

from sources.google_drive import GoogleDriveClient
from shared.utils.client import request_get, RequestException
from shared.utils.helpers import batch_iter
from shared.database.models import Order
from sources import repository as repo
from shared.utils.timezone import now_local_with_tz


class LoaderError(Exception):
    pass


class Loader:

    URL_CBR = 'https://www.cbr.ru/scripts/XML_daily.asp'
    FILE_NAME_TEST = 'test_kanalservis'
    MIME_TYPE_EXCEL = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    VALUTE_ID = 'R01235'
    MAX_BATCH_COUNT = 20
    DECIMAL_PLACES = 2

    def __init__(
            self,
            logger: logging.Logger = None,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._google_drive_client = GoogleDriveClient(logger=self._logger)

    def load_data(self) -> None:
        """
        Загрузка данных из гугл таблицы.
        Сохранение в БД.
        """
        file_id = self._get_file_id_by_name(self.FILE_NAME_TEST)
        file_obj = self._google_drive_client.export_file(file_id, self.MIME_TYPE_EXCEL)
        df = pd.read_excel(file_obj, converters={'стоимость,$': self._value_to_decimal})
        mapping_cols = {
            '№': 'number',
            'заказ №': 'order_number',
            'стоимость,$': 'price_usd',
            'срок поставки': 'delivery_time',
            }
        rate = self._get_rate_from_cbr()
        df = df.rename(columns=mapping_cols)

        df['price_rur'] = df.apply(
            lambda row: (row.price_usd * rate).quantize(Decimal(1).scaleb(
                -self.DECIMAL_PLACES), rounding=ROUND_DOWN),
            axis=1
            )
        loaded_at = now_local_with_tz()
        df['loaded_at'] = loaded_at
        data = df.to_dict('records')
        for batch_data in batch_iter(data, batch_size=self.MAX_BATCH_COUNT):
            repo.save_data_by_model_with_update(batch_data, Order)
        repo.delete_orders(loaded_at)

    def _get_rate_from_cbr(self) -> Decimal:
        """Получение курса валюты."""
        def _find_and_get_text_by_tag(root, tag):
            element = root.find(tag)
            if element is not None:
                return element.text
            else:
                raise ValueError(f'Does not exists tag {tag}')
        try:
            response = request_get(self.URL_CBR)
        except RequestException as e:
            raise LoaderError('Error request to CBR') from e

        root_el = ETree.fromstring(response.text)
        find_query = f"Valute[@ID='{self.VALUTE_ID}']"
        try:
            valute = root_el.find(find_query)
            value = _find_and_get_text_by_tag(valute, 'Value')
        except ValueError as e:
            raise LoaderError from e
        value = self._value_to_decimal(value)
        return value

    def _get_file_id_by_name(self, name: str) -> str:
        query = f"name='{name}'"
        files = self._google_drive_client.search_files(query, files_fields=['id', 'name', 'mimeType'])
        if len(files) > 1:
            msg_log = f'Found {len(files)} folders named {name}'
            raise LoaderError(msg_log)
        return files[0]['id']

    @staticmethod
    def _value_to_decimal(value: Any) -> Decimal:
        try:
            if isinstance(value, str) and ',' in value:
                value = value.replace(',', '.')
            return Decimal(value)
        except (ValueError, TypeError, InvalidOperation) as e:
            msg_log = f'Invali convert to decimal value: {value}'
            raise LoaderError(msg_log) from e


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Loader().load_data()
