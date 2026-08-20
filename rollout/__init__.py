from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from lab.constants import PRODUCTS, ROUTES
from lab.paths import ROLLOUT_STATE, STATE_DIR, TEMP_CAPS
from lab.copy import RETURN_TO_CURRENT


@dataclass
class RolloutConfig:
    route: str
    product_type: str
    status: str  # TESTING | PAUSED | CURRENT_PRICING
    traffic_percent: int  # 0, 5, 20, 50, 100; shadow is separate
    shadow: bool
    allowed_min: float
    allowed_max: float

    def assignment_mode(self) -> str:
        if self.status in {"PAUSED", "CURRENT_PRICING"} or self.traffic_percent <= 0:
            return "return_to_current"
        if self.shadow:
            return "shadow"
        return str(self.traffic_percent)


def default_configs() -> list[RolloutConfig]:
    configs = []
    for route in ROUTES:
        for product in PRODUCTS:
            shadow = not (route == "AUH-LHR" and product == "extra_legroom")
            configs.append(
                RolloutConfig(
                    route=route,
                    product_type=product,
                    status="TESTING",
                    traffic_percent=20 if not shadow else 0,
                    shadow=shadow,
                    allowed_min=80 if product == "extra_legroom" else 60,
                    allowed_max=150 if product == "extra_legroom" else 180,
                )
            )
    return configs


def load_configs() -> list[RolloutConfig]:
    if not ROLLOUT_STATE.exists():
        cfgs = default_configs()
        save_configs(cfgs)
        return cfgs
    raw = json.loads(ROLLOUT_STATE.read_text(encoding="utf-8"))
    return [RolloutConfig(**row) for row in raw]


def save_configs(configs: list[RolloutConfig]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ROLLOUT_STATE.write_text(
        json.dumps([asdict(c) for c in configs], indent=2), encoding="utf-8"
    )


def get_config(route: str, product_type: str) -> RolloutConfig:
    for cfg in load_configs():
        if cfg.route == route and cfg.product_type == product_type:
            return cfg
    cfgs = load_configs()
    fresh = RolloutConfig(
        route=route,
        product_type=product_type,
        status="TESTING",
        traffic_percent=20,
        shadow=False,
        allowed_min=80,
        allowed_max=150,
    )
    cfgs.append(fresh)
    save_configs(cfgs)
    return fresh


def upsert_config(updated: RolloutConfig) -> None:
    cfgs = load_configs()
    out = []
    found = False
    for cfg in cfgs:
        if cfg.route == updated.route and cfg.product_type == updated.product_type:
            out.append(updated)
            found = True
        else:
            out.append(cfg)
    if not found:
        out.append(updated)
    save_configs(out)


def assign_new_model(booking_id: str, cfg: RolloutConfig, salt: str = "lab-v1") -> bool:
    if cfg.status in {"PAUSED", "CURRENT_PRICING"}:
        return False
    if cfg.shadow:
        return False
    pct = int(cfg.traffic_percent)
    if pct <= 0:
        return False
    if pct >= 100:
        return True
    digest = hashlib.sha256(f"{salt}:{booking_id}:{cfg.route}:{cfg.product_type}".encode()).hexdigest()
    bucket = int(digest[:8], 16) % 100
    return bucket < pct


def is_shadow(cfg: RolloutConfig) -> bool:
    return bool(cfg.shadow) and cfg.status == "TESTING"


@dataclass
class TemporaryCapRecord:
    route: str
    product_type: str
    max_price: float
    until: str  # ISO date


def load_caps() -> list[TemporaryCapRecord]:
    if not TEMP_CAPS.exists():
        return []
    raw = json.loads(TEMP_CAPS.read_text(encoding="utf-8"))
    return [TemporaryCapRecord(**row) for row in raw]


def save_caps(caps: list[TemporaryCapRecord]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_CAPS.write_text(json.dumps([asdict(c) for c in caps], indent=2), encoding="utf-8")


def active_caps(today: date | None = None) -> list[TemporaryCapRecord]:
    today = today or date.today()
    out = []
    for cap in load_caps():
        if date.fromisoformat(cap.until) >= today:
            out.append(cap)
    return out
