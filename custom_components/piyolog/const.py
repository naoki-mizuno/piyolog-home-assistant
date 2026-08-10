"""Constants for the PiyoLog integration."""

from typing import NamedTuple, Optional

# Import classes from client.py to avoid duplication
from .client import (
    EventType,
    PoopAmount,
    PoopHardness,
    PoopColor,
    BreastfeedingOrder,
    POOP_AMOUNT_MAP,
    POOP_HARDNESS_MAP,
    POOP_COLOR_MAP,
    BREASTFEEDING_ORDER_MAP,
)

DOMAIN = "piyolog"

# Configuration keys
CONF_USER_ID = "user_id"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_TOKEN = "client_token"
CONF_DEFAULT_BABY_ID = "default_baby_id"
CONF_SYNC_INTERVAL = "sync_interval"

# Default values
DEFAULT_SYNC_INTERVAL = 30  # seconds
MIN_SYNC_INTERVAL = 30
MAX_SYNC_INTERVAL = 300

DEFAULT_MILK_AMOUNT = 100  # ml

# API constants
API_BASE_URL = "https://api2.piyolog.com"
API_VERSION = 2.0
API_SECRET = "NewPiyoLogApp"

# Service names of the events whose payload needs a hand-written handler; the
# straightforward ones are generated from ADD_EVENT_SERVICES below.
SERVICE_ADD_POO = "add_poo"
SERVICE_ADD_PEE_AND_POO = "add_pee_and_poo"
SERVICE_ADD_BREASTFEEDING = "add_breastfeeding"
SERVICE_ADD_WEIGHT = "add_weight"
SERVICE_ADD_CUSTOM = "add_custom"
SERVICE_FORCE_SYNC = "force_sync"
SERVICE_DELETE_MOST_RECENT_EVENT = "delete_most_recent_event"

# Default and upper-bound (minutes) for the delete_most_recent_event guard:
# events older than the chosen value (by created_at) are not eligible.
DEFAULT_DELETE_MAX_AGE_MINUTES = 10
MAX_DELETE_MAX_AGE_MINUTES = 180

# Custom event numbers PiyoLog supports (add_custom's "number" field).
MIN_CUSTOM_EVENT_NUMBER = 1
MAX_CUSTOM_EVENT_NUMBER = 10

# add_weight's "unit" field -> (divisor to kilograms, event "amount").  Weight is
# always stored in kg; amount is the flag telling the app to show the value in
# grams, which is how PiyoLog itself records a weight typed in grams.  It is the
# only measurement with such a flag -- height and the circumferences are plain
# centimeters.
WEIGHT_UNITS = {
    "kg": (1, 0),
    "g": (1000, 1),
}

# Sanity bound (kg) on a converted weight, so "3500" with the unit left at kg
# is rejected instead of silently logged as 3500 kg.
MAX_WEIGHT_KG = 100

# Event type to name mapping (for firing HA events in Phase 3)
EVENT_TYPE_NAMES = {
    EventType.OTHER: "other",
    EventType.MOTHERS_MILK: "breastfeeding",
    EventType.MILK: "milk",
    EventType.MILKING: "expressed_milk",
    EventType.SLEEP_BEGIN: "sleep",
    EventType.SLEEP_END: "wake_up",
    EventType.PEE: "pee",
    EventType.POO: "poo",
    EventType.BODY_TEMPERATURE: "body_temperature",
    EventType.MEAL: "baby_food",
    EventType.BODY_HEIGHT: "height",
    EventType.BODY_WEIGHT: "weight",
    EventType.COUGH: "cough",
    EventType.VOMITING: "vomit",
    EventType.RASH: "rash",
    EventType.INJURY: "injury",
    EventType.BATH: "bath",
    EventType.SNACK: "snack",
    EventType.MEAL2: "meal",
    EventType.DRINK: "drink",
    EventType.MEDICINE: "medicine",
    EventType.HOSPITAL: "hospital",
    EventType.WALKING: "walk",
    EventType.PUMPING: "pumping",
    EventType.CUSTOM1: "custom1",
    EventType.CUSTOM2: "custom2",
    EventType.CUSTOM3: "custom3",
    EventType.CUSTOM4: "custom4",
    EventType.CUSTOM5: "custom5",
    EventType.VACCINE: "vaccine",
    EventType.CUSTOM6: "custom6",
    EventType.CUSTOM7: "custom7",
    EventType.CUSTOM8: "custom8",
    EventType.CUSTOM9: "custom9",
    EventType.CUSTOM10: "custom10",
    EventType.MILESTONE: "milestone",
    EventType.HEAD: "head_circumference",
    EventType.CHEST: "chest_circumference",
    EventType.MEMO: "memo",
}

# Attribute names for service calls
ATTR_BABY_ID = "baby_id"
ATTR_BABY_INDEX = "baby_index"
ATTR_DATETIME = "datetime"
ATTR_MEMO = "memo"
ATTR_AMOUNT = "amount"
ATTR_POO_AMOUNT = "poo_amount"
ATTR_POO_HARDNESS = "poo_hardness"
ATTR_POO_COLOR = "poo_color"
ATTR_BREASTFEEDING_LEFT_MINUTES = "breastfeeding_left_minutes"
ATTR_BREASTFEEDING_RIGHT_MINUTES = "breastfeeding_right_minutes"
ATTR_BREASTFEEDING_ORDER = "breastfeeding_order"
ATTR_EVENT_TYPE = "event_type"
ATTR_MAX_AGE_MINUTES = "max_age_minutes"
ATTR_SYNC_BEFORE_CHECK = "sync_before_check"
ATTR_TEMPERATURE = "temperature"
ATTR_HEIGHT = "height"
ATTR_WEIGHT = "weight"
ATTR_CIRCUMFERENCE = "circumference"
ATTR_UNIT = "unit"
ATTR_DURATION_MINUTES = "duration_minutes"
ATTR_CUSTOM_NUMBER = "number"


class EventField(NamedTuple):
    """The one numeric input an add_* service accepts, and where it is stored.

    PiyoLog keeps every measurement in the same two generic event columns, so
    which of them an event type uses depends on the type (see
    swagger/swagger.yaml, BabyEvent.amount / BabyEvent.value).
    """

    attr: str  # service field name
    event_field: str  # "amount" or "value" on the PiyoLog event
    scale: float = 1.0  # multiplier from the service's unit to PiyoLog's
    required: bool = False
    default: Optional[float] = None


# Event registration services that need no special handling: service name ->
# (EventType, numeric field or None). They all take the common baby_id /
# baby_index / datetime / memo arguments on top of the field listed here.
ADD_EVENT_SERVICES: dict[str, tuple[int, Optional[EventField]]] = {
    # Diapers
    "add_pee": (EventType.PEE, None),
    # Sleep
    "add_sleep": (EventType.SLEEP_BEGIN, None),
    "add_wake_up": (EventType.SLEEP_END, None),
    # Feeding
    "add_milk": (
        EventType.MILK,
        EventField(ATTR_AMOUNT, "amount", default=DEFAULT_MILK_AMOUNT),
    ),
    "add_expressed_milk": (
        EventType.MILKING,
        EventField(ATTR_AMOUNT, "amount", required=True),
    ),
    "add_pumping": (
        EventType.PUMPING,
        EventField(ATTR_AMOUNT, "amount", required=True),
    ),
    "add_drink": (EventType.DRINK, EventField(ATTR_AMOUNT, "amount")),
    "add_baby_food": (EventType.MEAL, None),
    "add_meal": (EventType.MEAL2, None),
    "add_snack": (EventType.SNACK, None),
    # Growth
    "add_temperature": (
        EventType.BODY_TEMPERATURE,
        EventField(ATTR_TEMPERATURE, "value", required=True),
    ),
    "add_height": (
        EventType.BODY_HEIGHT,
        EventField(ATTR_HEIGHT, "value", required=True),
    ),
    "add_head_circumference": (
        EventType.HEAD,
        EventField(ATTR_CIRCUMFERENCE, "value", required=True),
    ),
    "add_chest_circumference": (
        EventType.CHEST,
        EventField(ATTR_CIRCUMFERENCE, "value", required=True),
    ),
    # Health
    "add_cough": (EventType.COUGH, None),
    "add_vomit": (EventType.VOMITING, None),
    "add_rash": (EventType.RASH, None),
    "add_injury": (EventType.INJURY, None),
    "add_medicine": (EventType.MEDICINE, None),
    "add_hospital": (EventType.HOSPITAL, None),
    "add_vaccine": (EventType.VACCINE, None),
    # Daily life
    "add_bath": (EventType.BATH, None),
    "add_walk": (
        EventType.WALKING,
        EventField(ATTR_DURATION_MINUTES, "value", scale=60),
    ),
    "add_milestone": (EventType.MILESTONE, None),
    "add_note": (EventType.MEMO, None),
    "add_other": (EventType.OTHER, None),
}

# EventType int for each custom event number (PiyoLog splits them into two
# non-contiguous ranges, 24-28 and 30-34).
CUSTOM_EVENT_TYPES = {
    1: EventType.CUSTOM1,
    2: EventType.CUSTOM2,
    3: EventType.CUSTOM3,
    4: EventType.CUSTOM4,
    5: EventType.CUSTOM5,
    6: EventType.CUSTOM6,
    7: EventType.CUSTOM7,
    8: EventType.CUSTOM8,
    9: EventType.CUSTOM9,
    10: EventType.CUSTOM10,
}

# Map from delete-service event_type selector value to EventType int. Every
# type PiyoLog can store is filterable, under the same names the integration
# uses for its piyolog_event_* Home Assistant events.
DELETE_EVENT_TYPE_MAP = {
    name: event_type for event_type, name in EVENT_TYPE_NAMES.items()
}

# Every service the integration registers (used when unloading the last entry).
ALL_SERVICES = [
    *ADD_EVENT_SERVICES,
    SERVICE_ADD_POO,
    SERVICE_ADD_PEE_AND_POO,
    SERVICE_ADD_BREASTFEEDING,
    SERVICE_ADD_WEIGHT,
    SERVICE_ADD_CUSTOM,
    SERVICE_FORCE_SYNC,
    SERVICE_DELETE_MOST_RECENT_EVENT,
]
