"""Test Bosch water heater."""
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from custom_components.bosch.const import DOMAIN, CONF_PROTOCOL, CONF_DEVICE_TYPE, ACCESS_TOKEN, ACCESS_KEY, UUID
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD, ATTR_TEMPERATURE
from homeassistant.util import dt as dt_util
from datetime import timedelta

async def test_water_heater_entity(hass):
    """Test water heater entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_ADDRESS: "demo",
            ACCESS_TOKEN: "demo",
            ACCESS_KEY: "demo_key",
            CONF_PASSWORD: "demo",
            CONF_DEVICE_TYPE: "IVT",
            CONF_PROTOCOL: "HTTP",
            UUID: "123456789-demo",
        }
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Trigger update to ensure entities are initialized
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()

    state = hass.states.get("water_heater.dhw1")
    assert state is not None
    assert state.state == "performance"
    assert state.attributes["current_temperature"] == 56.6
    assert state.attributes["temperature"] == 48.0

    # Test set temperature
    await hass.services.async_call(
        "water_heater",
        "set_temperature",
        {"entity_id": "water_heater.dhw1", ATTR_TEMPERATURE: 50.0},
        blocking=True,
    )