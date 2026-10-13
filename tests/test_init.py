"""Tests for setting up and unloading the RME infrared integration."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.rme_infrared.const import DOMAIN


async def test_setup_and_unload(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """The entry loads and unloads cleanly."""
    assert init_integration.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()
    assert init_integration.state is ConfigEntryState.NOT_LOADED


async def test_device(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """One RME device is registered for the entry."""
    devices = dr.async_entries_for_config_entry(
        dr.async_get(hass), init_integration.entry_id
    )
    assert len(devices) == 1
    device = devices[0]
    assert device.identifiers == {(DOMAIN, init_integration.entry_id)}
    assert device.manufacturer == "RME"
    assert device.name == "RME ADI-2 DAC"
    assert device.model == "ADI-2 DAC / DAC FS"
