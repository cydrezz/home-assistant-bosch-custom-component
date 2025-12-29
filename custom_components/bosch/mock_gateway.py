"""Mock Gateway for Bosch Custom Component."""
from bosch_thermostat_client.const import HC, DHW, SENSOR, SC, RECORDING, HVAC_HEAT, VALUE, UNITS, NAME, REGULAR, BINARY
from bosch_thermostat_client.const.ivt import INVALID
from bosch_thermostat_client.const.easycontrol import DV
from homeassistant.util import dt as dt_util
from datetime import timedelta
from .const import SWITCH

class MockObject:
    """Base Mock Object."""
    def __init__(self, attr_id, name):
        self.attr_id = attr_id
        self.name = name
        self.id = attr_id
        self.parent_id = None
        self.update_initialized = True
        self.path = attr_id  # Path for debugging

    async def update(self, **kwargs):
        pass

    async def fetch_range(self, start_time, stop_time):
        return {}

    def get_value(self, key, default=None):
        return default

class MockSensor(MockObject):
    """Mock Sensor."""
    def __init__(self, attr_id, name, state, units=None, kind=REGULAR):
        super().__init__(attr_id, name)
        self.state = state
        self.unit_of_measurement = units
        self.kind = kind
        self.state_message = str(state)
        self.device_class = None
        self.state_class = None
        self.entity_category = None
        
        # Auto-detect device class and state class based on units
        if self.unit_of_measurement == "C":
            self.device_class = "temperature"
            self.state_class = "measurement"
        elif self.unit_of_measurement == "%":
            self.state_class = "measurement"
        elif self.unit_of_measurement in ("kWh", "Wh"):
            self.device_class = "energy"
            self.state_class = "total_increasing"

    def get_property(self, attr_id):
        val = self.state
        if self.kind == RECORDING:
            now = dt_util.now()
            last_hour = (now - timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )
            val = [{"d": last_hour, VALUE: self.state}]
        return {
            VALUE: val,
            UNITS: self.unit_of_measurement,
            INVALID: False,
            NAME: self.name,
        }

class MockSwitch(MockObject):
    """Mock Switch."""
    def __init__(self, attr_id, name, state):
        super().__init__(attr_id, name)
        self.state = state

    async def turn_on(self):
        self.state = True

    async def turn_off(self):
        self.state = False

class MockCircuit(MockObject):
    """Mock Circuit."""
    def __init__(self, name, attr_id, kind=HC):
        super().__init__(attr_id, name)
        self.kind = kind
        self.setpoint = 21.5
        self.schedule = None
        self.extra_state_attributes = {}
        self.support_presets = False
        self.hvac_action = HVAC_HEAT
        self.hvac_modes = ["heat", "off"]
        self.ha_modes = ["heat", "off"]
        self.ha_mode = "heat"
        self.preset_modes = []
        self.preset_mode = None
        self.temp_units = "C"
        self.target_temperature = 21.5
        self.current_temp = 27.9
        self.state = "heat"
        self.min_temp = 5
        self.max_temp = 30
        self.sensors = []
        self.regular_switches = []
        self.number_switches = []
        self.switches = [] # Selects

    async def set_temperature(self, temperature):
        self.target_temperature = temperature

    async def set_ha_mode(self, mode):
        self.ha_mode = mode
        self.state = mode
        return 1

class MockDhwCircuit(MockCircuit):
    """Mock DHW Circuit."""
    def __init__(self, name, attr_id):
        super().__init__(name, attr_id, kind=DHW)
        self.setpoint = 48.0
        self.target_temperature = 48.0
        self.current_temp = 56.6
        self.support_target_temp = True
        self.ha_modes = ["performance", "off"]
        self.ha_mode = "performance"
        self.state = "performance"
        self.min_temp = 30
        self.max_temp = 80

    async def set_temperature(self, temperature):
        self.target_temperature = temperature

class MockBoschGateway:
    """Mock Gateway."""

    def __init__(self, host, **kwargs):
        """Initialize mock."""
        self.host = host
        self.device_name = "RC300"
        self.device_model = "IVT"
        self.device_type = "RC300"
        self.firmware = "04.08.02"
        self.uuid = "123456789-demo"
        self.bus_type = "RC300/RC310/Nefit Moduline 3000"
        self.access_key = "demo_key"
        self.access_token = "demo"
        self.database = {"mock": "data"}
        self._initialized = False
        
        # Global Sensors
        self._sensors = [
            MockSensor("actualHeatingPumpModulation", "Actual heating pump modulation", "0.0", "%"),
            MockSensor("actualModulation", "Actual modulation", "57.0", "%"),
            MockSensor("actualPower", "Actual Power", "1.5", "kW"),
            MockSensor("actualSupplyTemperature", "Actual supply temp", "27.8", "C"),
            MockSensor("supplyTemperature", "Actual Supply temperature", "27.8", "C"),
            MockSensor("chimneySweeper", "ChimneySweeper", "Off"),
            MockSensor("energyConsumption", "Energy consumption", "88319072.0", "kWh"),
            MockSensor("flameStatus", "flameStatus", "Off"),
            MockSensor("healthStatus", "Health status", "ok"),
            MockSensor("hotWaterTemperature", "Hotwater temp", "45.0", "C"),
            MockSensor("notifications", "Notifications", "No notifications"),
            MockSensor("numberOfStarts", "numberOfStarts", "5735"),
            MockSensor("outdoorTemperature", "Outdoor temperature", "3.5", "C"),
            MockSensor("poolTemperature", "Pool temperature", "0.0", "C"),
            MockSensor("returnTemperature", "Return temp", "27.9", "C"),
            MockSensor("startTime", "Start time", "2025-06-02T14:42:11"),
            MockSensor("supplyTemperatureSetpoint", "Supply temp setpoint", "33.0", "C"),
            MockSensor("switchTemperature", "Switch temp", "27.8", "C"),
            MockSensor("systemUptime", "Total system uptime", "35701048"),
            MockSensor("commonFault", "Common Fault", "off", kind=BINARY),
            # Recording Sensors
            MockSensor("ractualTemp", "ractualTemp", 55.0, "C", kind=RECORDING),
            MockSensor("rcompressor", "rcompressor", 2.0, "kWh", kind=RECORDING),
            MockSensor("rconsumedEnergy", "rconsumedEnergy", 2.0, "kWh", kind=RECORDING),
            MockSensor("reheater", "reheater", 0.0, "kWh", kind=RECORDING),
            MockSensor("routdoor_t1", "routdoor_t1", 5.0, "C", kind=RECORDING),
            MockSensor("routputProduced", "routputProduced", 7.0, "kWh", kind=RECORDING),
            MockSensor("rroomtemperature", "rroomtemperature", 21.5, "C", kind=RECORDING),
            MockSensor("rsolarYield", "rsolarYield", 10.5, "Wh", kind=RECORDING),
        ]

        self._switches = [
            MockSwitch("testSwitch", "Test Switch", False)
        ]

        # HC1
        hc1 = MockCircuit("hc1", "hc1")
        hc1.sensors = [
            MockSensor("hc1_actualSupplyTemperature", "Actual supply temperature", "27.9", "C"),
            MockSensor("hc1_currentRoomSetpoint", "Current room setpoint", "21.5", "C"),
            MockSensor("hc1_currentSummerWinterMode", "Current Summer Winter Mode", "forced"),
            MockSensor("hc1_pumpModulation", "Pump Modulation", "0.0", "%"),
            MockSensor("hc1_summerWinterSwitchMode", "Summer Winter Switchmode", "automatic"),
            MockSensor("hc1_summerWinterThreshold", "Summer Winter Threshold", "18.0", "C"),
            MockSensor("hc1_supplyTemperatureSetpoint", "Supply Temperature Setpoint", "33.0", "C"),
        ]
        for s in hc1.sensors:
            s.parent_id = hc1.id
        self._hc = [hc1]

        # SC1
        sc1 = MockCircuit("sc1", "sc1", kind=SC)
        sc1.sensors = [
            MockSensor("sc1_actuatorStatus", "Actuator Status", "yes"),
            MockSensor("sc1_collectorTemperature", "Collector Temperature", "0.5", "C"),
            MockSensor("sc1_dhwTankTemperature", "DHW Tank Temperature", "55.0", "C"),
            MockSensor("sc1_pumpModulation", "Pump Modulation", "0.0", "%"),
            MockSensor("sc1_solarYield", "Solar Yield", "0.0", "Wh"),
        ]
        for s in sc1.sensors:
            s.parent_id = sc1.id
        self._sc = [sc1]

        # DHW1
        dhw1 = MockDhwCircuit("dhw1", "dhw1")
        dhw1.sensors = [
             MockSensor("chargeDuration", "Charge duration", "180.0", "mins"),
             MockSensor("chargeSetpoint", "Charge setpoint", "70.0", "C"),
        ]
        for s in dhw1.sensors:
            s.parent_id = dhw1.id
        self._dhw = [dhw1]

    async def check_connection(self):
        """Mock check connection."""
        return self.uuid

    async def custom_initialize(self, db):
        """Mock initialize."""
        pass

    async def get_capabilities(self):
        """Mock capabilities."""
        return [HC, DHW, SENSOR, SC, RECORDING, DV, SWITCH]

    async def check_firmware_validity(self):
        """Mock firmware check."""
        pass

    async def rawscan(self):
        """Mock rawscan."""
        return {"id": "demo"}

    async def close(self, force=False):
        """Mock close."""
        pass
    
    async def raw_put(self, path, value):
        pass

    async def raw_query(self, path):
        return "mock_value"
    
    @property
    def heating_circuits(self):
        return self._hc
        
    @property
    def dhw_circuits(self):
        return self._dhw
        
    @property
    def sensors(self):
        return self._sensors

    @property
    def regular_switches(self):
        return self._switches
        
    @property
    def binary_sensors(self):
        return []
    
    def get_circuits(self, c_type):
        return {
            HC: self._hc,
            DHW: self._dhw,
            SC: self._sc,
            DV: [],
        }.get(c_type, [])