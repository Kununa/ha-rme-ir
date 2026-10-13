"""Button platform for the RME infrared integration."""

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_MODEL, KEY_NAMES, MODELS, RmeKey
from .entity import RmeIrEntity

PARALLEL_UPDATES = 1

# These live on the media player instead.
MEDIA_PLAYER_KEYS = {
    RmeKey.POWER_OFF,
    RmeKey.VOLUME_UP,
    RmeKey.VOLUME_DOWN,
    RmeKey.MUTE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one button per IR code the model supports."""
    codes = MODELS[entry.data[CONF_MODEL]].codes
    async_add_entities(
        RmeIrButton(entry, key, codes[key])
        for key in RmeKey
        if key in codes and key not in MEDIA_PLAYER_KEYS
    )


class RmeIrButton(RmeIrEntity, ButtonEntity):
    """A button that sends one RME IR code."""

    def __init__(self, entry: ConfigEntry, key: RmeKey, code: int) -> None:
        """Initialize the button."""
        super().__init__(entry, key.value)
        self._code = code
        self.entity_description = ButtonEntityDescription(
            key=key.value, name=KEY_NAMES[key]
        )

    async def async_press(self) -> None:
        """Send the code."""
        await self._send_code(self._code)
