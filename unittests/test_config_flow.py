"""Test Bosch config flow."""
from unittest.mock import patch, MagicMock, AsyncMock
from homeassistant import config_entries, data_entry_flow
from custom_components.bosch.const import DOMAIN, CONF_PROTOCOL
from bosch_thermostat_client.const.ivt import IVT

async def test_flow_user(hass):
    """Test that user flow works."""
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

    # Mock the gateway
    mock_gateway = MagicMock()
    mock_gateway.check_connection = AsyncMock(return_value="123456789")
    mock_gateway.uuid = "123456789"
    mock_gateway.device_name = "Test Device"
    mock_gateway.host = "1.2.3.4"
    mock_gateway.access_key = "key"
    mock_gateway.access_token = "token"
    
    # Mock gateway_chooser to return a class that returns our mock_gateway
    mock_gateway_cls = MagicMock(return_value=mock_gateway)

    with patch("custom_components.bosch.config_flow.gateway_chooser", return_value=mock_gateway_cls), \
         patch("custom_components.bosch.async_setup_entry", return_value=True):
        
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "address": "1.2.3.4",
                "access_token": "token",
                "password": "password"
            }
        )
    
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Device"
    assert result["data"]["address"] == "1.2.3.4"
    
    await hass.async_block_till_done()
