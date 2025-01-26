import pytest_asyncio
from typing import AsyncGenerator
from mockhass import MockHomeAssistant
from pathlib import Path


@pytest_asyncio.fixture
async def hass() -> AsyncGenerator[MockHomeAssistant]:
    config_dir = Path(__file__).parent.parent / "homeassistant"
    hass = MockHomeAssistant(config_dir.absolute())
    await hass.async_start()
    yield hass
    await hass.check_assertions()

    await hass.async_stop()