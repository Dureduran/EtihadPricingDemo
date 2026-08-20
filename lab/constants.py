ROUTES = ("AUH-LHR", "AUH-JFK", "AUH-BOM", "AUH-CDG", "AUH-SYD")
PRODUCTS = ("extra_baggage", "extra_legroom")
FARE_TYPES = ("Basic", "Value", "Comfort", "Deluxe")
LOYALTY = ("None", "Silver", "Gold", "Platinum")
CHANNELS = ("web", "app", "airport")
CABINS = ("Economy", "Business")

LONG_HAUL = frozenset({"AUH-JFK", "AUH-SYD", "AUH-LHR"})

# Portfolio stand-in: which fare already includes the product.
FARE_INCLUDES = {
    "Basic": set(),
    "Value": {"extra_baggage"},
    "Comfort": {"extra_baggage"},
    "Deluxe": {"extra_baggage", "extra_legroom"},
}

# Gold+ complimentary extra-legroom on Economy is a stand-in, not Etihad production.
COMPLIMENTARY_SEAT_TIERS = frozenset({"Gold", "Platinum"})

ROUTE_HAUL_HOURS = {
    "AUH-BOM": 3.0,
    "AUH-CDG": 7.0,
    "AUH-LHR": 7.5,
    "AUH-JFK": 14.0,
    "AUH-SYD": 14.5,
}

CURRENT_BASE_AED = {
    "AUH-BOM": {"extra_baggage": 85, "extra_legroom": 95},
    "AUH-CDG": {"extra_baggage": 110, "extra_legroom": 125},
    "AUH-LHR": {"extra_baggage": 115, "extra_legroom": 130},
    "AUH-JFK": {"extra_baggage": 140, "extra_legroom": 165},
    "AUH-SYD": {"extra_baggage": 150, "extra_legroom": 175},
}

MIN_PRICE = {"extra_baggage": 40, "extra_legroom": 50}
MAX_PRICE = {"extra_baggage": 220, "extra_legroom": 280}
SAFE_FIXED = {"extra_baggage": 75, "extra_legroom": 95}

PRICE_GRIDS = {
    "extra_baggage": list(range(40, 221, 10)),
    "extra_legroom": list(range(50, 281, 10)),
}

FIXTURE_BOOKING = {
    "booking_id": "FIX-AUH-LHR-001",
    "route": "AUH-LHR",
    "fare_type": "Basic",
    "loyalty": "None",
    "channel": "web",
    "cabin": "Economy",
    "days_to_departure": 4,
    "remaining_extra_legroom": 7,
    "party_size": 1,
    "product_type": "extra_legroom",
}

TRAINING_FEATURES = [
    "route",
    "fare_type",
    "loyalty",
    "channel",
    "cabin",
    "days_to_departure",
    "remaining_extra_legroom",
    "party_size",
    "product_type",
    "displayed_price",
]

TARGET = "purchased"
GENERATOR_ONLY = ("latent_wtp", "generator_rule_id", "true_elasticity")

ROLLOUT_STEPS = (
    "offline",
    "shadow",
    "5",
    "20",
    "50",
    "100",
    "return_to_current",
)
