"""Common fixtures for the RME infrared tests."""

from infrared_protocols.commands import Command as InfraredCommand
from infrared_protocols.commands.nec import NECCommand
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.infrared import InfraredEmitterEntity
from homeassistant.components.infrared.const import DATA_COMPONENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from custom_components.rme_infrared.const import (
    CONF_ADDRESS,
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"

EMITTER_ENTITY_ID = "infrared.test_ir_emitter"
ADDRESS = 0x3412


class MockInfraredEmitterEntity(InfraredEmitterEntity):
    """Infrared emitter that records the commands it is asked to send."""

    _attr_has_entity_name = True
    _attr_name = "Test IR emitter"

    def __init__(self, unique_id: str) -> None:
        """Initialize the mock emitter."""
        self._attr_unique_id = unique_id
        self.send_command_calls: list[InfraredCommand] = []

    async def async_send_command(self, command: InfraredCommand) -> None:
        """Record the command."""
        self.send_command_calls.append(command)

    def sent_codes(self) -> list[tuple[int, int]]:
        """Return (address, command) of every NEC command sent."""
        assert all(isinstance(c, NECCommand) for c in self.send_command_calls)
        return [(c.address, c.command) for c in self.send_command_calls]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load integrations from custom_components."""


@pytest.fixture
async def mock_emitter(hass: HomeAssistant) -> MockInfraredEmitterEntity:
    """Set up the infrared domain with one emitter entity."""
    assert await async_setup_component(hass, "infrared", {})
    await hass.async_block_till_done()
    entity = MockInfraredEmitterEntity("test_ir_emitter")
    await hass.data[DATA_COMPONENT].async_add_entities([entity])
    assert entity.entity_id == EMITTER_ENTITY_ID
    return entity


@pytest.fixture
def model() -> str:
    """Return the RME model key to configure. Override via parametrize."""
    return "adi2_dac"


@pytest.fixture
def mock_config_entry(model: str) -> MockConfigEntry:
    """Return a config entry for the selected model."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"RME {model} via Test IR emitter",
        data={
            CONF_MODEL: model,
            CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
            CONF_ADDRESS: f"{ADDRESS:X}",
        },
        unique_id=f"{model}_{EMITTER_ENTITY_ID}",
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    mock_config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up the integration with the mock emitter."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry


def entity_id_for(hass: HomeAssistant, domain: str, entry_id: str, suffix: str) -> str:
    """Look up an entity_id by the integration's unique_id scheme."""
    entity_id = er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, f"{entry_id}_{suffix}"
    )
    assert entity_id is not None, f"no {domain} entity with suffix {suffix}"
    return entity_id
