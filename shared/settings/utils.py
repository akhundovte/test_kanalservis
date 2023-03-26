import yaml

from typing import Union
from pathlib import Path


def get_config(path: Union[str, Path]):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config
