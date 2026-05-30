from __future__ import annotations

import abc
import pandas as pd


class BaseReport(abc.ABC):
    """Contract that every ARI report must satisfy.

    Subclasses implement `run()` and return a tidy DataFrame whose columns
    are ready to be exported directly to Excel.
    """

    #: Short, filesystem-safe name used as the default Excel sheet name.
    name: str = ""

    @abc.abstractmethod
    def run(self) -> pd.DataFrame:
        """Collect data and return it as a pandas DataFrame."""
