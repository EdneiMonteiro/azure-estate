"""Timestamp appended to every exported file name.

The agreed format is ``<nome>_DD_MM_AAAA_HH_MM_SS`` — for example
``resource_groups_21_08_2026_19_45_20``.

The stamp is computed **once per process** on purpose: a single run of
``--report all`` writes dozens of files, and a per-file timestamp would let
them drift across seconds, breaking the visual pairing between the ``.xlsx``
and the ``.csv`` of the same report.
"""
from __future__ import annotations

from datetime import datetime

STAMP_FORMAT = "%d_%m_%Y_%H_%M_%S"

_RUN_STAMP = datetime.now().strftime(STAMP_FORMAT)


def run_stamp() -> str:
    """Return the timestamp shared by every file of the current run."""
    return _RUN_STAMP
