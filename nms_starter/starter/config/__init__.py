from .types import init_types
from retry import retry


@retry(tries=3, delay=2)
def init_config():
    init_types()

