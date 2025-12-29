"""Test Bosch switch."""
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from custom_components.bosch.const import DOMAIN, SWITCH, CONF_PROTOCOL, CONF_DEVICE_TYPE, ACCESS_TOKEN, ACCESS_KEY, UUID
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD
from homeassistant.util import dt as dt_util
from datetime import timedelta
from unittest.mock import patch, MagicMock, AsyncMock

async def test_switch_entity(hass):
    """Test switch entity."""
    
    # Create the gateway mock we want to use
    gateway = MagicMock()
    gateway.uuid = "123456789-demo"
    gateway.firmware = "1.0.0"
    gateway.device_name = "Mock Device"
    gateway.device_model = "Mock Model"
    gateway.device_type = "Mock Type"
    gateway.bus_type = "CAN"
    gateway.database = {"mock": "database"}
    gateway.check_connection = AsyncMock(return_value=True)
    gateway.async_init = AsyncMock(return_value=True)
    gateway.get_capabilities = AsyncMock(return_value=["switch"]) # Only switch for this test
    gateway.close = AsyncMock()
    gateway.custom_initialize = AsyncMock()
    
    # Setup switch on the gateway
    switch1 = MagicMock()
    switch1.name = "Test Switch"
    switch1.attr_id = "testSwitch"
    switch1.id = "testSwitch"
    switch1.state = False
    switch1.parent_id = None
    switch1.update = AsyncMock()
    switch1.turn_on = AsyncMock()
    switch1.turn_off = AsyncMock()
    
    gateway.regular_switches = [switch1]
    gateway.switches = [switch1] # Just in case
    gateway.sensors = []
    gateway.binary_sensors = []
    gateway.heating_circuits = []
    gateway.dhw_circuits = []
    
    MockGatewayClass = MagicMock(return_value=gateway)
    
    # Patch gateway_chooser to return our MockGatewayClass
    with patch("bosch_thermostat_client.gateway_chooser", return_value=MockGatewayClass):
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
                SWITCH: ["testSwitch"]
            }
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Trigger update to ensure entities are initialized
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
        await hass.async_block_till_done()

        print(f"All states: {hass.states.async_all()}")
        state = hass.states.get("switch.test_switch")
        assert state is not None
