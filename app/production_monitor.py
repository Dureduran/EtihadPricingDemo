from __future__ import annotations

from typing import Any

import pandas as pd

from app.pricing_controls import DEFAULT_PRODUCT, DEFAULT_ROUTE, pause_controls, return_to_current_pricing
from monitor.health import health

SECTIONS = (
    "Commercial performance",
    "Model health",
    "System health",
    "Business rules",
)


def monitor_report(offers: pd.DataFrame) -> dict[str, Any]:
    return health(offers)


def pause_from_monitor(route: str = DEFAULT_ROUTE, product_type: str = DEFAULT_PRODUCT):
    return pause_controls(route, product_type)


def return_to_current_from_monitor(route: str = DEFAULT_ROUTE, product_type: str = DEFAULT_PRODUCT):
    return return_to_current_pricing(route, product_type)
