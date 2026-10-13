"""Common entity for the RME infrared integration."""

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_ADDRESS, CONF_INFRARED_ENTITY_ID, CONF_MODEL, DOMAIN, MODELS


class RmeIrEntity(InfraredEmitterConsumerEntity):
    """Base entity providing device info and IR sending."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, unique_id_suffix: str) -> None:
        """Initialize the entity."""
        self._infrared_emitter_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
        self._address = int(entry.data[CONF_ADDRESS], 16)
        self._model = MODELS[entry.data[CONF_MODEL]]
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"RME {self._model.name.split(' / ')[0]}",
            manufacturer="RME",
            model=self._model.name,
        )

    async def _send_code(self, code: int) -> None:
        """Send one NEC command code."""
        await self._send_command(NECCommand(address=self._address, command=code))
