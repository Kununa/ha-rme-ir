"""Tests for the RME infrared media player."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_INPUT_SOURCE_LIST,
    ATTR_MEDIA_VOLUME_MUTED,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_SELECT_SOURCE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_UP,
)
from homeassistant.const import (
    ATTR_ASSUMED_STATE,
    ATTR_ENTITY_ID,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from .conftest import ADDRESS, EMITTER_ENTITY_ID, MockInfraredEmitterEntity, entity_id_for


def _player(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    return entity_id_for(hass, MEDIA_PLAYER_DOMAIN, entry.entry_id, "media_player")


async def _call(hass: HomeAssistant, service: str, entity_id: str, **data) -> None:
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        service,
        {ATTR_ENTITY_ID: entity_id, **data},
        blocking=True,
    )


@pytest.mark.parametrize(
    ("model", "entity_id", "sources"),
    [
        ("adi2_dac", "media_player.rme_adi_2_dac", ["Coaxial", "Optical", "USB"]),
        (
            "adi2_pro",
            "media_player.rme_adi_2_pro_fs",
            ["AES", "S/PDIF coaxial", "Optical", "Analog", "USB"],
        ),
    ],
)
async def test_entity(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_id: str,
    sources: list[str],
) -> None:
    """The media player starts on (assumed state) with the model's inputs."""
    assert _player(hass, init_integration) == entity_id
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON
    assert state.attributes[ATTR_ASSUMED_STATE] is True
    assert state.attributes[ATTR_INPUT_SOURCE_LIST] == sources


@pytest.mark.parametrize(
    ("model", "service", "data", "code"),
    [
        ("adi2_dac", SERVICE_TURN_ON, {}, 0x20),
        ("adi2_dac", SERVICE_TURN_OFF, {}, 0x14),
        ("adi2_dac", SERVICE_VOLUME_UP, {}, 0x22),
        ("adi2_dac", SERVICE_VOLUME_DOWN, {}, 0x21),
        ("adi2_dac", SERVICE_VOLUME_MUTE, {ATTR_MEDIA_VOLUME_MUTED: True}, 0x2A),
        ("adi2_dac", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "Coaxial"}, 0x23),
        ("adi2_dac", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "Optical"}, 0x24),
        ("adi2_dac", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "USB"}, 0x25),
        ("adi2_pro", SERVICE_TURN_ON, {}, 0xA0),
        ("adi2_pro", SERVICE_TURN_OFF, {}, 0x94),
        ("adi2_pro", SERVICE_VOLUME_UP, {}, 0xA2),
        ("adi2_pro", SERVICE_VOLUME_DOWN, {}, 0xA1),
        ("adi2_pro", SERVICE_VOLUME_MUTE, {ATTR_MEDIA_VOLUME_MUTED: False}, 0xAA),
        ("adi2_pro", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "AES"}, 0x95),
        ("adi2_pro", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "Analog"}, 0x98),
        ("adi2_pro", SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "USB"}, 0x99),
    ],
)
async def test_action_sends_code(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
    service: str,
    data: dict,
    code: int,
) -> None:
    """Each action sends exactly one NEC command with the configured address."""
    await _call(hass, service, _player(hass, init_integration), **data)
    assert mock_emitter.sent_codes() == [(ADDRESS, code)]


async def test_power_state(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Turning off/on updates the assumed state."""
    entity_id = _player(hass, init_integration)

    await _call(hass, SERVICE_TURN_OFF, entity_id)
    assert hass.states.get(entity_id).state == STATE_OFF

    await _call(hass, SERVICE_TURN_ON, entity_id)
    assert hass.states.get(entity_id).state == STATE_ON


async def test_select_source_updates_state(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """The selected input is remembered."""
    entity_id = _player(hass, init_integration)
    await _call(hass, SERVICE_SELECT_SOURCE, entity_id, **{ATTR_INPUT_SOURCE: "USB"})
    assert hass.states.get(entity_id).attributes[ATTR_INPUT_SOURCE] == "USB"


async def test_availability_follows_emitter(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """The player is unavailable while its IR transmitter is."""
    entity_id = _player(hass, init_integration)

    hass.states.async_set(EMITTER_ENTITY_ID, STATE_UNAVAILABLE)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE

    hass.states.async_set(EMITTER_ENTITY_ID, "2026-10-14T00:00:00.000+00:00")
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON
