"""Test Bosch switch."""
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from custom_components.bosch.const import DOMAIN, SWITCH, CONF_PROTOCOL, CONF_DEVICE_TYPE, ACCESS_TOKEN, ACCESS_KEY, UUID
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD, STATE_OFF, STATE_ON
from homeassistant.util import dt as dt_util
from datetime import timedelta

async def test_switch_entity(hass):
    """Test switch entity."""
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

    state = hass.states.get("switch.test_switch")
    assert state is not None
    assert state.state == STATE_OFF

    # Turn On
    await hass.services.async_call(
        "switch",
        "turn_on",
        {"entity_id": "switch.test_switch"},
        blocking=True,
    )
    state = hass.states.get("switch.test_switch")
    assert state.state == STATE_ON