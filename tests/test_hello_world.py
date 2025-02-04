from mockhass import MockHomeAssistant
import pytest

@pytest.mark.asyncio
async def test_hello_world(hass: MockHomeAssistant) -> None:
    hass.states.async_set("sensor.test_temperature", 23.0)
    hass.assert_entity("sensor.test_temperature").equals("23.0")


@pytest.mark.asyncio
async def test_hello_world_again(hass: MockHomeAssistant) -> None:
    """The same test to check for issues with isolation."""
    hass.states.async_set("sensor.test_temperature", 23.0)
    hass.assert_entity("sensor.test_temperature").equals("23.0")