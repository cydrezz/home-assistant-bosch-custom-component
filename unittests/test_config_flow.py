"""Test Bosch config flow."""
import threading
from unittest.mock import MagicMock

# Patch threading.Thread to prevent slixmpp from starting its shutdown loop thread
# This must be done before importing bosch_thermostat_client
_original_thread_init = threading.Thread.__init__

def _mock_thread_init(self, *args, **kwargs):
    _original_thread_init(self, *args, **kwargs)
    if "_run_safe_shutdown_loop" in self.name:
        self.start = lambda: None  # Disable start method for this thread

# Apply the patch
threading.Thread.__init__ = _mock_thread_init

from unittest.mock import patch
from homeassistant import config_entries, data_entry_flow
from custom_components.bosch.const import DOMAIN, CONF_PROTOCOL
from bosch_thermostat_client.const.ivt import IVT

async def test_flow_demo_mode(hass):
    """Test that demo mode works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "choose_type"

    # Select IVT
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={"device_type": IVT}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "protocol"

    # Select HTTP
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_PROTOCOL: "HTTP"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "http_config"

    # Enter Demo Credentials
    with patch("custom_components.bosch.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "address": "demo",
                "access_token": "demo",
                "password": "demo"
            }
        )
    
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "RC300"
    assert result["data"]["address"] == "demo"
    await hass.async_block_till_done()
