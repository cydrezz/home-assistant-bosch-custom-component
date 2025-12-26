"""Test Bosch sensors."""
from datetime import timedelta
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from custom_components.bosch.const import DOMAIN, SENSORS, CONF_PROTOCOL, CONF_DEVICE_TYPE, ACCESS_TOKEN, ACCESS_KEY, UUID
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD, UnitOfTemperature
from homeassistant.util import dt as dt_util

async def test_sensor_mock_values(hass):
    """Test that sensors are created with mock values."""
    # Setup the config entry with demo credentials
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
            SENSORS: ["actualSupplyTemperature", "outdoorTemperature"]
        }
    )
    entry.add_to_hass(hass)

    # Load the integration
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    
    # Advance time to trigger the initial update (clears lingering timer and updates entities)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()

    # Check Actual Supply Temperature (Mock value: 27.8)
    state = hass.states.get("sensor.actual_supply_temp")
    assert state is not None
    assert state.state == "27.8"
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    # Check Outdoor Temperature (Mock value: 3.5)
    state = hass.states.get("sensor.outdoor_temperature")
    assert state is not None
    assert state.state == "3.5"
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS