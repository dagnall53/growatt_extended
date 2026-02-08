import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "growatt_extended"
GROWATT_DOMAIN = "growatt_server"


class GrowattExtendedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Growatt Extended."""

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            entry_id = user_input["entry_id"]

            growatt_entries = [
                e for e in self.hass.config_entries.async_entries(GROWATT_DOMAIN)
            ]

            if not growatt_entries:
                errors["base"] = "no_growatt"
            elif not any(e.entry_id == entry_id for e in growatt_entries):
                errors["base"] = "invalid_entry"
            else:
                return self.async_create_entry(
                    title="Growatt Extended Sensors",
                    data={"entry_id": entry_id},
                )

        growatt_entries = self.hass.config_entries.async_entries(GROWATT_DOMAIN)
        entry_ids = {e.entry_id: f"{e.title} ({e.entry_id})" for e in growatt_entries}

        schema = vol.Schema({
            vol.Required("entry_id"): vol.In(entry_ids)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
