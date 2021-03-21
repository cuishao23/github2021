import threading
import logging
from retry import retry
from .bmc_import import bmc_importer
from .luban_import import luban_importer, luban_bak_importer
from .warning_settings_import import warning_settings_importer
from .terminal_type_import import terminal_type_importer
from dao.nms_redis import nms_is_first_import, flush_redis_db, set_nms_first_import, clean_up_tmp_db
from config.common import LOGGING


logger = logging.getLogger(LOGGING['loggername'])


@retry(logger=logger, delay=2, max_delay=30, backoff=2)
def init_importer():
    if nms_is_first_import():
        logger.info('first import ...')
        flush_redis_db()
        luban_importer()
        bmc_importer()
        warning_settings_importer()
        terminal_type_importer()
        logger.info('import ok!')
        set_nms_first_import()
    else:
        clean_up_tmp_db()
        logger.info('not need to import!')


__all__ = ('init_importer')
