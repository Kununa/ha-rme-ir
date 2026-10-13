"""Tests for the RME infrared config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.rme_infrared.const import (
    CONF_ADDRESS,
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
)

from .conftest import EMITTER_ENTITY_ID


@pytest.fixture(autouse=True)
def mock_setup_entry():
    """Don't set up the entry the flow creates."""
    with patch(
        "custom_components.rme_infrared.async_setup_entry", AsyncMock(return_value=True)
    ) as mock:
        yield mock


def _user_input(model: str = "adi2_dac", address: str = "3412") -> dict[str, str]:
    return {
        CONF_MODEL: model,
        CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
        CONF_ADDRESS: address,
    }


async def test_abort_without_emitters(hass: HomeAssistant) -> None:
    """The flow aborts when no IR transmitter exists."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


@pytest.mark.usefixtures("mock_emitter")
@pytest.mark.parametrize(
    ("model", "title"),
    [
        ("adi2_dac", "RME ADI-2 DAC / DAC FS via Test IR emitter"),
        ("adi2_pro", "RME ADI-2 Pro FS / Pro FS R via Test IR emitter"),
    ],
)
async def test_create_entry(
    hass: HomeAssistant, mock_setup_entry: AsyncMock, model: str, title: str
) -> None:
    """A valid form creates an entry for the chosen model."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input(model)
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == title
    assert result["data"] == _user_input(model)
    assert result["result"].unique_id == f"{model}_{EMITTER_ENTITY_ID}"
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.usefixtures("mock_emitter")
async def test_address_is_normalized(hass: HomeAssistant) -> None:
    """The address is stored as upper-case hex without leading zeros."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input(address="0x00ab")
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ADDRESS] == "AB"


@pytest.mark.usefixtures("mock_emitter")
@pytest.mark.parametrize("address", ["xyz", "", "10000", "-1"])
async def test_invalid_address(hass: HomeAssistant, address: str) -> None:
    """An address that isn't 16-bit hex shows an error, then can be fixed."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input(address=address)
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_ADDRESS: "invalid_address"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input()
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.usefixtures("mock_emitter")
async def test_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """The same model on the same transmitter can only be added once."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input()
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("mock_emitter")
async def test_other_model_same_emitter_allowed(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """A different model may share a transmitter with an existing entry."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_input(model="adi2_pro")
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
