import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "growatt_extended"
GROWATT_DOMAIN = "growatt_server"


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up via YAML (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the extended Growatt sensors from a config entry."""

    growatt_entry_id = entry.data["entry_id"]

    # Retrieve the official Growatt Server config entry
    growatt_entry = hass.config_entries.async_get_entry(growatt_entry_id)

    if growatt_entry is None:
        raise RuntimeError(
            f"Growatt Extended: No config entry found for entry_id {growatt_entry_id}"
        )

    # The official integration exposes its coordinator here:
    # runtime_data.total_coordinator
    runtime_data = getattr(growatt_entry, "runtime_data", None)

    if runtime_data is None:
        raise RuntimeError(
            f"Growatt Extended: runtime_data is None for entry_id {growatt_entry_id}"
        )

    coordinator = getattr(runtime_data, "total_coordinator", None)

    if coordinator is None:
        raise RuntimeError(
            f"Growatt Extended: total_coordinator missing in runtime_data for entry_id {growatt_entry_id}"
        )

    # Store coordinator for sensor platform
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "growatt_entry_id": growatt_entry_id,
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload the extended integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
