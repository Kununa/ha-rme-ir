"""Tests for the RME infrared buttons."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.rme_infrared.const import MODELS

from .conftest import ADDRESS, MockInfraredEmitterEntity, entity_id_for


def _buttons(hass: HomeAssistant, entry: MockConfigEntry) -> list[er.RegistryEntry]:
    return [
        e
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        if e.domain == BUTTON_DOMAIN
    ]


@pytest.mark.parametrize(
    ("model", "count"),
    [
        # Every code except inputs (media player) and power off/volume/mute.
        ("adi2_dac", 44),
        ("adi2_pro", 48),
    ],
)
async def test_button_count(
    hass: HomeAssistant, init_integration: MockConfigEntry, model: str, count: int
) -> None:
    """One button per remaining code of the model."""
    buttons = _buttons(hass, init_integration)
    assert len(buttons) == count
    keys = {e.unique_id.removeprefix(f"{init_integration.entry_id}_") for e in buttons}
    assert keys <= {k.value for k in MODELS[model].codes}
    assert not keys & {"power_off", "volume_up", "volume_down", "mute"}


@pytest.mark.parametrize(
    ("model", "key", "entity_id", "code"),
    [
        ("adi2_dac", "power_toggle", "button.rme_adi_2_dac_power_toggle", 0x20),
        ("adi2_dac", "setup_7", "button.rme_adi_2_dac_setup_7", 0x3C),
        ("adi2_dac", "dac_nos", "button.rme_adi_2_dac_dac_filter_nos", 0x12),
        ("adi2_dac", "mono", "button.rme_adi_2_dac_mono", 0x00),
        ("adi2_pro", "sel", "button.rme_adi_2_pro_fs_sel", 0xB5),
        ("adi2_pro", "remap_5", "button.rme_adi_2_pro_fs_remap_5_coax_key", 0xA3),
        ("adi2_pro", "crossfeed_3", "button.rme_adi_2_pro_fs_crossfeed_3", 0x8B),
    ],
)
async def test_press_sends_code(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
    key: str,
    entity_id: str,
    code: int,
) -> None:
    """Pressing a button sends its NEC code."""
    assert entity_id_for(hass, BUTTON_DOMAIN, init_integration.entry_id, key) == entity_id

    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    assert mock_emitter.sent_codes() == [(ADDRESS, code)]


@pytest.mark.parametrize("model", list(MODELS))
async def test_every_button_sends_its_table_code(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
    model: str,
) -> None:
    """Every button of every model sends exactly the code from its table."""
    codes = MODELS[model].codes
    for entry in _buttons(hass, init_integration):
        key = entry.unique_id.removeprefix(f"{init_integration.entry_id}_")
        mock_emitter.send_command_calls.clear()
        await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entry.entity_id}, blocking=True
        )
        assert mock_emitter.sent_codes() == [(ADDRESS, codes[key])], key
