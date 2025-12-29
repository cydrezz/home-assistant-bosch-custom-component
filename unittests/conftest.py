"""Global fixtures for Bosch integration."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from bosch_thermostat_client.const import BINARY, SENSOR, HC, DHW, SWITCH

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield

@pytest.fixture(autouse=True)
def mock_bosch_gateway_fixture():
    """Mock the Bosch Gateway for all tests."""
    with patch("bosch_thermostat_client.gateway_chooser") as mock_chooser:
        MockGatewayClass = MagicMock()
        gateway = MagicMock()
        print(f"DEBUG: Configured gateway id={id(gateway)}")
        
        # Basic attributes
        gateway.uuid = "123456789-demo"
        gateway.firmware = "1.0.0"
        gateway.device_name = "Mock Device"
        gateway.device_model = "Mock Model"
        gateway.device_type = "Mock Type"
        gateway.bus_type = "CAN"
        gateway.database = {"mock": "database"}
        
        # Async methods
        gateway.check_connection = AsyncMock(return_value=True)
        gateway.async_init = AsyncMock(return_value=True)
        gateway.get_capabilities = AsyncMock(return_value=[HC, DHW, SENSOR, SWITCH])
        gateway.close = AsyncMock()
        gateway.custom_initialize = AsyncMock()
        
        # Sensors
        sensor1 = MagicMock()
        sensor1.kind = "regular"
        sensor1.name = "Actual Supply Temp"
        sensor1.attr_id = "actualSupplyTemperature"
        sensor1.id = "actualSupplyTemperature"
        sensor1.state = "27.8"
        sensor1.units = "°C"
        sensor1.device_class = "temperature"
        sensor1.state_class = "measurement"
        sensor1.entity_category = None
        sensor1.parent_id = None
        sensor1.update = AsyncMock()
        sensor1.get_property.return_value = {"value": "27.8", "unitOfMeasure": "C"}

        sensor2 = MagicMock()
        sensor2.kind = "regular"
        sensor2.name = "Outdoor Temperature"
        sensor2.attr_id = "outdoorTemperature"
        sensor2.id = "outdoorTemperature"
        sensor2.state = "3.5"
        sensor2.units = "°C"
        sensor2.device_class = "temperature"
        sensor2.state_class = "measurement"
        sensor2.entity_category = None
        sensor2.parent_id = None
        sensor2.update = AsyncMock()
        sensor2.get_property.return_value = {"value": "3.5", "unitOfMeasure": "C"}
        
        binary_sensor = MagicMock()
        binary_sensor.kind = BINARY
        binary_sensor.name = "Common Fault"
        binary_sensor.attr_id = "commonFault"
        binary_sensor.id = "commonFault"
        binary_sensor.state = "off"
        binary_sensor.device_class = None
        binary_sensor.state_class = None
        binary_sensor.entity_category = None
        binary_sensor.parent_id = None
        binary_sensor.update = AsyncMock()
        binary_sensor.get_property.return_value = {}
        
        gateway.sensors = [sensor1, sensor2, binary_sensor]
        
        # Switches
        switch1 = MagicMock()
        switch1.kind = "regular" # Added kind
        switch1.name = "Test Switch"
        switch1.attr_id = "testSwitch"
        switch1.id = "testSwitch"
        switch1.state = False
        switch1.device_class = None
        switch1.state_class = None
        switch1.entity_category = None
        switch1.parent_id = None
        switch1.update = AsyncMock()
        switch1.get_property.return_value = {} # Added get_property
        
        async def turn_on():
            switch1.state = True
        async def turn_off():
            switch1.state = False
            
        switch1.turn_on = AsyncMock(side_effect=turn_on)
        switch1.turn_off = AsyncMock(side_effect=turn_off)
        
        gateway.switches = [switch1]
        
        # Heating Circuits
        mock_hc = MagicMock()
        mock_hc.name = "Heating Circuit 1"
        mock_hc.attr_id = "hc1"
        mock_hc.id = "hc1"
        mock_hc.update = AsyncMock()
        mock_hc.current_temp = 27.9
        mock_hc.target_temperature = 21.5
        mock_hc.min_temp = 5
        mock_hc.max_temp = 30
        mock_hc.ha_mode = "heat"
        mock_hc.ha_modes = ["heat", "off", "auto"]
        mock_hc.support_target_temp = True
        mock_hc.support_presets = False
        mock_hc.device_class = None
        mock_hc.state_class = None
        mock_hc.entity_category = None
        
        # HC Sensor
        sensor_hc = MagicMock()
        sensor_hc.kind = "regular"
        sensor_hc.name = "Actual Supply Temperature"
        sensor_hc.attr_id = "actualSupplyTemperature"
        sensor_hc.id = "actualSupplyTemperature"
        sensor_hc.state = "27.9"
        sensor_hc.units = "°C"
        sensor_hc.device_class = "temperature"
        sensor_hc.state_class = "measurement"
        sensor_hc.entity_category = None
        sensor_hc.parent_id = "hc1"
        sensor_hc.update = AsyncMock()
        sensor_hc.get_property.return_value = {"value": "27.9", "unitOfMeasure": "C"}
        
        mock_hc.sensors = [sensor_hc]
        
        async def set_hc_temp(temp):
            mock_hc.target_temperature = temp
            
        mock_hc.set_temperature = AsyncMock(side_effect=set_hc_temp)
        mock_hc.set_hvac_mode = AsyncMock()
        mock_hc.extra_state_attributes = {}
        mock_hc.schedule = None
        mock_hc.parent_id = None
        mock_hc.temp_units = "C"
        
        gateway.heating_circuits = [mock_hc]
        
        # DHW Circuits
        mock_dhw = MagicMock()
        mock_dhw.name = "DHW Circuit 1"
        mock_dhw.attr_id = "dhw1"
        mock_dhw.id = "dhw1"
        mock_dhw.update = AsyncMock()
        mock_dhw.current_temp = 40.0
        mock_dhw.target_temperature = 50.0
        mock_dhw.min_temp = 30.0
        mock_dhw.max_temp = 70.0
        mock_dhw.ha_mode = "performance"
        mock_dhw.ha_modes = ["performance", "off", "high"]
        mock_dhw.support_target_temp = True
        mock_dhw.support_presets = False
        mock_dhw.device_class = None
        mock_dhw.state_class = None
        mock_dhw.entity_category = None
        
        async def set_dhw_temp(temp):
            mock_dhw.target_temperature = temp
            
        mock_dhw.set_temperature = AsyncMock(side_effect=set_dhw_temp)
        mock_dhw.set_operation_mode = AsyncMock()
        mock_dhw.extra_state_attributes = {}
        mock_dhw.schedule = None
        mock_dhw.parent_id = None
        mock_dhw.temp_units = "C"
        
        gateway.dhw_circuits = [mock_dhw]
        
        MockGatewayClass.return_value = gateway
        mock_chooser.return_value = MockGatewayClass
        
        yield gateway
