"""Test Bosch component setup."""
from homeassistant.setup import async_setup_component
from custom_components.bosch.const import DOMAIN

async def test_async_setup(hass):
    """Test the component gets setup."""
    config = {DOMAIN: {}}
    assert await async_setup_component(hass, DOMAIN, config) is True
