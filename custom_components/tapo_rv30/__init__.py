"""Tapo RV20 or RV30 Robot Vacuum integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .aes_client import AesVacuumClient
from .const import CONF_TRANSPORT, DEFAULT_PORT, DOMAIN, TRANSPORT_AES, TRANSPORT_TPAP
from .coordinator import TapoCoordinator
from .tpap import TapoVacuumClient

PLATFORMS = [
    Platform.VACUUM, Platform.SENSOR, Platform.CAMERA, Platform.SELECT,
    Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BUTTON,
]


def _build_client(entry: ConfigEntry):
    """Instantiate the right transport client for this entry.

    Existing config entries created before transport auto-detection was
    added won't have CONF_TRANSPORT set — default those to TPAP so
    upgrading the integration doesn't break already-working setups.
    """
    transport = entry.data.get(CONF_TRANSPORT, TRANSPORT_TPAP)
    kwargs = dict(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        port=DEFAULT_PORT,
    )
    if transport == TRANSPORT_AES:
        return AesVacuumClient(**kwargs)
    return TapoVacuumClient(**kwargs)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = _build_client(entry)
    coordinator = TapoCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
