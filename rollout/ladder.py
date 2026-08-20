from __future__ import annotations

from dataclasses import replace

from lab.constants import ROLLOUT_STEPS
from rollout import RolloutConfig, get_config, upsert_config

LADDER_STATES = ROLLOUT_STEPS
DISPLAY_STATES = (
    "Offline testing",
    "Shadow mode",
    "5%",
    "20%",
    "50%",
    "100%",
    "Return to Current Pricing",
)
STATUSES = ("TESTING", "PAUSED", "CURRENT_PRICING")


def current_step(cfg: RolloutConfig) -> str:
    if cfg.status in {"PAUSED", "CURRENT_PRICING"}:
        return "return_to_current"
    if cfg.shadow:
        return "shadow"
    if cfg.traffic_percent <= 0:
        return "offline"
    if cfg.traffic_percent >= 100:
        return "100"
    return str(int(cfg.traffic_percent))


def apply_step(cfg: RolloutConfig, step: str) -> RolloutConfig:
    if step not in LADDER_STATES:
        raise ValueError(f"unknown ladder step: {step}")
    if step == "offline":
        return replace(cfg, shadow=False, traffic_percent=0, status="TESTING")
    if step == "shadow":
        return replace(cfg, shadow=True, traffic_percent=0, status="TESTING")
    if step == "return_to_current":
        return replace(cfg, shadow=False, traffic_percent=0, status="CURRENT_PRICING")
    pct = int(step)
    return replace(cfg, shadow=False, traffic_percent=pct, status="TESTING")


def set_step(route: str, product_type: str, step: str) -> RolloutConfig:
    updated = apply_step(get_config(route, product_type), step)
    upsert_config(updated)
    return updated
