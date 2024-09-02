
from dataclasses import dataclass
from enum import Enum
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()


class ResponseMode(Enum):
    full = 'full'
    default = 'default'