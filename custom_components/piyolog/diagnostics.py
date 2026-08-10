"""Diagnostics support for the PiyoLog integration.

Home Assistant picks this module up automatically and adds a "Download
diagnostics" entry to the integration's config-entry menu (Settings ->
Devices & Services -> PiyoLog -> ... -> Download diagnostics). The download
is a single JSON file containing the entire PiyoLog dataset.

WARNING: nothing is redacted. The file contains the account credentials
(user_id, client_id, client_token) and every event ever recorded. Anyone
holding it has full access to the PiyoLog account -- never attach it to a
public issue.
"""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return the complete PiyoLog dataset plus coordinator state.

    The snapshot is a fresh full sync (all babies, all events, including
    soft-deleted ones), not just what the coordinator keeps in memory.
    """
    entry_data = hass.data[DOMAIN][entry.entry_id]
    client = entry_data["client"]
    coordinator = entry_data["coordinator"]

    try:
        snapshot = await hass.async_add_executor_job(client.full_snapshot)
    except Exception as err:  # diagnostics must produce a file, not an error
        snapshot = {"error": f"{type(err).__name__}: {err}"}

    return {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval_seconds": (
                coordinator.update_interval.total_seconds()
                if coordinator.update_interval
                else None
            ),
            "main_version": client._main_version,
            "minor_version": client._minor_version,
            "babies": coordinator._babies_cache,
            "tracked_counts": {
                "last_events": len(coordinator._last_events),
                "sleep_begin_events": len(coordinator._sleep_begin_events),
                "breastfeeding_events": len(coordinator._breastfeeding_events),
                "recent_events": len(coordinator._recent_events),
                "seen_event_ids": len(coordinator._seen_event_ids),
            },
        },
        "snapshot": snapshot,
    }
