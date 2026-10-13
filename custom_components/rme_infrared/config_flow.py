"""Config flow for the RME infrared integration."""

from typing import Any

try:
    import probatio as vol
except ImportError:  # older Home Assistant
    import voluptuous as vol

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_ADDRESS,
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DEFAULT_ADDRESS,
    DOMAIN,
    MODELS,
)


class RmeIrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for RME IR."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the device model, the IR emitter and the NEC address."""
        emitters = async_get_emitters(self.hass)
        if not emitters:
            return self.async_abort(reason="no_emitters")

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                address = int(user_input[CONF_ADDRESS], 16)
                if not 0 <= address <= 0xFFFF:
                    raise ValueError
            except ValueError:
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                model = user_input[CONF_MODEL]
                emitter = user_input[CONF_INFRARED_ENTITY_ID]
                await self.async_set_unique_id(f"{model}_{emitter}")
                self._abort_if_unique_id_configured()
                name = emitter
                if state := self.hass.states.get(emitter):
                    name = state.name or emitter
                return self.async_create_entry(
                    title=f"RME {MODELS[model].name} via {name}",
                    data={
                        CONF_MODEL: model,
                        CONF_INFRARED_ENTITY_ID: emitter,
                        CONF_ADDRESS: f"{address:X}",
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODEL): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=key, label=model.name)
                                for key, model in MODELS.items()
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain=INFRARED_DOMAIN, include_entities=emitters
                        )
                    ),
                    vol.Required(CONF_ADDRESS, default=DEFAULT_ADDRESS): str,
                }
            ),
            errors=errors,
        )
