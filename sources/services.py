import logging.config

from sources.loader import Loader, LoaderError
from sources.google_drive import GoogleDriveClientError
from shared.settings.config import get_settings_logging


logging.config.dictConfig(get_settings_logging('loader'))
logger = logging.getLogger(__name__)


def load_orders():
    logger.info(f'Start load_orders')
    try:
        Loader(logger=logger).load_data()
    except (LoaderError, GoogleDriveClientError) as e:
        msg = f'{e.__class__.__name__} during processing load orders\n{e}'
        logger.error(msg, exc_info=True)
        raise e
    logger.info(f'End load_orders')


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    load_orders()
