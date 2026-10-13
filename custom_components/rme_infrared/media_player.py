"""Media player platform for the RME infrared integration."""

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import RmeKey
from .entity import RmeIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the RME media player."""
    async_add_entities([RmeIrMediaPlayer(entry)])


class RmeIrMediaPlayer(RmeIrEntity, MediaPlayerEntity):
    """RME device controlled over IR (assumed state)."""

    _attr_name = None
    _attr_assumed_state = True
    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the media player."""
        super().__init__(entry, "media_player")
        self._attr_source_list = list(self._model.sources)
        self._attr_state = MediaPlayerState.ON

    async def async_turn_on(self) -> None:
        """Power on (the RME 'Power' key is a toggle)."""
        await self._send_code(self._model.codes[RmeKey.POWER_TOGGLE])
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Power off with the dedicated discrete off code."""
        await self._send_code(self._model.codes[RmeKey.POWER_OFF])
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Volume up."""
        await self._send_code(self._model.codes[RmeKey.VOLUME_UP])

    async def async_volume_down(self) -> None:
        """Volume down."""
        await self._send_code(self._model.codes[RmeKey.VOLUME_DOWN])

    async def async_mute_volume(self, mute: bool) -> None:
        """Toggle mute (the device only exposes a toggle)."""
        await self._send_code(self._model.codes[RmeKey.MUTE])

    async def async_select_source(self, source: str) -> None:
        """Select an input."""
        await self._send_code(self._model.sources[source])
        self._attr_source = source
        self.async_write_ha_state()
