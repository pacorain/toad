import pytest_asyncio
import os
from homeassistant.core import HomeAssistant
from typing import AsyncGenerator
from typing import Any


class TestHomeAssistant(HomeAssistant):
    def assert_entity_is(self, sensor: str, attribute: str, expected: str = None):
        if expected is None:
            expected = attribute
            attribute = None

        state = self.states.get(sensor)
        if attribute:
            assert state.attributes.get(attribute) == expected
        else:
            assert state.state == expected


@pytest_asyncio.fixture
async def hass() -> AsyncGenerator[HomeAssistant]:
    hass = TestHomeAssistant(os.path.dirname(os.path.dirname(__file__)))
    await hass.async_start()
    yield hass
    assert False  # Test failure

    await hass.async_stop()