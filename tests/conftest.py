import pytest_asyncio
import os
from typing import AsyncGenerator
from mockhass import MockHomeAssistant


@pytest_asyncio.fixture
async def hass() -> AsyncGenerator[MockHomeAssistant]:
    hass = MockHomeAssistant(os.path.dirname(os.path.dirname(__file__)))
    await hass.async_start()
    yield hass
    await hass.check_assertions()

    await hass.async_stop()