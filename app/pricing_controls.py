from __future__ import annotations

from dataclasses import replace
from datetime import date

from rollout import (
    RolloutConfig,
    TemporaryCapRecord,
    get_config,
    load_caps,
    save_caps,
    upsert_config,
)
from rollout.ladder import apply_step, current_step, set_step

DEFAULT_ROUTE = "AUH-LHR"
DEFAULT_PRODUCT = "extra_legroom"
STATUSES = ("TESTING", "PAUSED", "CURRENT_PRICING")
TRAFFIC_STEPS = (0, 5, 20, 50, 100)


def default_route_product() -> tuple[str, str]:
    return DEFAULT_ROUTE, DEFAULT_PRODUCT


def load_controls(route: str = DEFAULT_ROUTE, product_type: str = DEFAULT_PRODUCT) -> RolloutConfig:
    return get_config(route, product_type)


def save_controls(
    cfg: RolloutConfig,
    *,
    status: str,
    traffic_percent: int,
    allowed_min: float,
    allowed_max: float,
    shadow: bool = False,
) -> RolloutConfig:
    traffic = 0 if status != "TESTING" else int(traffic_percent)
    updated = replace(
        cfg,
        status=status,
        traffic_percent=traffic,
        allowed_min=float(allowed_min),
        allowed_max=float(allowed_max),
        shadow=bool(shadow),
    )
    upsert_config(updated)
    return get_config(updated.route, updated.product_type)


def increase_testing(route: str, product_type: str, step: str) -> RolloutConfig:
    if step not in {"5", "20", "50", "100"}:
        raise ValueError(f"not a live testing step: {step}")
    return set_step(route, product_type, step)


def pause_controls(route: str, product_type: str) -> RolloutConfig:
    cfg = get_config(route, product_type)
    upsert_config(replace(cfg, status="PAUSED", traffic_percent=0))
    return get_config(route, product_type)


def return_to_current_pricing(route: str, product_type: str) -> RolloutConfig:
    return set_step(route, product_type, "return_to_current")


def add_temporary_cap(
    route: str,
    product_type: str,
    max_price: float,
    until: date,
) -> list[TemporaryCapRecord]:
    caps = load_caps()
    caps.append(
        TemporaryCapRecord(
            route=route,
            product_type=product_type,
            max_price=float(max_price),
            until=until.isoformat(),
        )
    )
    save_caps(caps)
    return load_caps()


__all__ = [
    "DEFAULT_PRODUCT",
    "DEFAULT_ROUTE",
    "STATUSES",
    "TRAFFIC_STEPS",
    "add_temporary_cap",
    "apply_step",
    "current_step",
    "default_route_product",
    "increase_testing",
    "load_controls",
    "pause_controls",
    "return_to_current_pricing",
    "save_controls",
]
