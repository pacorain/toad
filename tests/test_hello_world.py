from tests.conftest import TestHomeAssistant
import pytest

@pytest.mark.asyncio
async def test_hello_world(hass: TestHomeAssistant) -> None:
    hass.states.async_set("sensor.test_temperature", 23.0)
    hass.assert_entity_is("sensor.test_temperature", "23.0")