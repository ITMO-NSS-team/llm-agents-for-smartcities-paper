from enum import Enum
import pathlib
from typing import Any, List

import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
ArrayLike = List[Any] | np.ndarray | pd.Series


class ResponseMode(Enum):
    full = "full"
    default = "default"
