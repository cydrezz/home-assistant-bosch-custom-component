"""Test Bosch climate."""
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from custom_components.bosch.const import DOMAIN, SENSORS, CONF_PROTOCOL, CONF_DEVICE_TYPE, ACCESS_TOKEN, ACCESS_KEY, UUID
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD, ATTR_TEMPERATURE
from homeassistant.components.climate import HVACMode, ClimateEntityFeature
from homeassistant.util import dt as dt_util
from datetime import timedelta

async def test_climate_entity(hass):
    """Test climate entity."""
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
            SENSORS: ["actualSupplyTemperature"],
        }
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Trigger update to ensure entities are initialized
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()

    state = hass.states.get("climate.heating_circuit_1")
    assert state is not None
    assert state.state == HVACMode.HEAT
    assert state.attributes["current_temperature"] == 27.9
    assert state.attributes["temperature"] == 21.5

    # Verify supported features include TURN_ON and TURN_OFF
    supported_features = state.attributes["supported_features"]
    assert supported_features & ClimateEntityFeature.TURN_OFF
    assert supported_features & ClimateEntityFeature.TURN_ON

    # Test set temperature
    await hass.services.async_call(
        "climate",
        "set_temperature",
        {"entity_id": "climate.heating_circuit_1", ATTR_TEMPERATURE: 23.0},
        blocking=True,
    )

    # Trigger update to refresh state from mock
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=70))
    await hass.async_block_till_done()
    
    state = hass.states.get("climate.heating_circuit_1")
    assert state.attributes["temperature"] == 23.0

    # Check that the circuit sensor also updated
    print(f"DEBUG: All states: {hass.states.async_all()}")
    # Note: The sensor ID depends on how the integration names it. 
    # Based on logs, it seems to be sensor.actual_supply_temp
    sensor_state = hass.states.get("sensor.actual_supply_temp")
    if sensor_state is None:
         # Fallback to check if it's prefixed
         sensor_state = hass.states.get("sensor.heating_circuit_1_actual_supply_temperature")
    
    assert sensor_state is not None
    assert sensor_state.state == "27.8"
