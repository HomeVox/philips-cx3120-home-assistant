"""Constants for the Philips CX3120 integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.const import Platform


DOMAIN = "philips_cx3120"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"

DEFAULT_NAME = "Philips 3000 Series Fan Heater"
DEFAULT_PORT = 5683
UPDATE_INTERVAL = timedelta(seconds=20)

MANUFACTURER = "Philips"
MODEL = "CX3120"

PLATFORMS: tuple[Platform, ...] = (
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
)

KEY_DEVICE_ID = "DeviceId"
KEY_NAME = "D01S03"
KEY_MODEL = "D01S05"
KEY_SW_VERSION = "D01S12"
KEY_POWER = "D03102"
KEY_CHILD_LOCK = "D03103"
KEY_MODE_A = "D0310A"
KEY_MODE_B = "D0310C"
KEY_TARGET_TEMPERATURE = "D0310E"
KEY_BEEP = "D03130"
KEY_ALT_CURRENT_TEMPERATURE = "D0313B"
KEY_HEATING_ACTION = "D0313F"
KEY_AUTO_PLUS_AI = "D03180"
KEY_OSCILLATION = "D0320F"
KEY_TIMER = "D03110"
KEY_REMAINING_TIME = "D03211"
KEY_CURRENT_TEMPERATURE = "D03224"
KEY_ERROR_CODE = "D03240"
KEY_RSSI = "rssi"
KEY_RUNTIME = "Runtime"
KEY_CONNECT_TYPE = "ConnectType"
KEY_WIFI_VERSION = "WifiVersion"
KEY_FREE_MEMORY = "free_memory"

PRESET_AUTO_PLUS = "auto_plus"
PRESET_VENTILATION = "ventilation"
PRESET_LOW = "low"
PRESET_MEDIUM = "medium"
PRESET_HIGH = "high"

PRESET_PATTERNS: dict[str, dict[str, Any]] = {
    PRESET_AUTO_PLUS: {KEY_POWER: 1, KEY_MODE_A: 3, KEY_MODE_B: 0},
    PRESET_VENTILATION: {KEY_POWER: 1, KEY_MODE_A: 1, KEY_MODE_B: -127},
    PRESET_LOW: {KEY_POWER: 1, KEY_MODE_A: 3, KEY_MODE_B: 66},
    PRESET_MEDIUM: {KEY_POWER: 1, KEY_MODE_A: 3, KEY_MODE_B: 67},
    PRESET_HIGH: {KEY_POWER: 1, KEY_MODE_A: 3, KEY_MODE_B: 65},
}

OSCILLATION_ON_VALUE = 45
OSCILLATION_OFF_VALUE = 0

BEEP_ON_VALUE = 100
BEEP_OFF_VALUE = 0

HEATING_ACTION_MAP: dict[int, str] = {
    65: "strong",
    67: "medium",
    68: "low",
    -16: "idle",
    0: "fan",
}

TIMER_MAP: dict[int, str] = {
    0: "Off",
    2: "1h",
    3: "2h",
    4: "3h",
    5: "4h",
    6: "5h",
    7: "6h",
    8: "7h",
    9: "8h",
    10: "9h",
    11: "10h",
    12: "11h",
    13: "12h",
}

TIMER_OPTION_TO_VALUE: dict[str, int] = {label: value for value, label in TIMER_MAP.items()}


def current_temperature_from_status(status: dict[str, Any]) -> float | None:
    """Return current temperature from raw device status."""
    raw = status.get(KEY_CURRENT_TEMPERATURE)
    if isinstance(raw, (int, float)):
        if abs(raw) >= 100:
            return float(raw) / 10.0
        return float(raw)

    raw_alt = status.get(KEY_ALT_CURRENT_TEMPERATURE)
    if isinstance(raw_alt, (int, float)):
        return float(raw_alt)

    return None


def preset_from_status(status: dict[str, Any]) -> str | None:
    """Return the active preset from raw device status."""
    for preset, pattern in PRESET_PATTERNS.items():
        if all(status.get(key) == value for key, value in pattern.items()):
            return preset
    return None


def heating_action_from_status(status: dict[str, Any]) -> str | None:
    """Return human-friendly heating action text."""
    raw = status.get(KEY_HEATING_ACTION)
    if raw is None:
        return None
    return HEATING_ACTION_MAP.get(raw, str(raw))


def timer_option_from_status(status: dict[str, Any]) -> str | None:
    """Return the active timer label from raw status."""
    raw = status.get(KEY_TIMER)
    if raw is None:
        return None
    return TIMER_MAP.get(raw, str(raw))


def title_from_status(status: dict[str, Any], fallback: str) -> str:
    """Build a friendly title from device status."""
    return str(status.get(KEY_NAME) or status.get(KEY_MODEL) or fallback)
