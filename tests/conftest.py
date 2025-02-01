import pytest_asyncio
import pytest
from typing import AsyncGenerator
from mockhass import MockHomeAssistant
from homeassistant import loader, config as conf_util, bootstrap
from pathlib import Path

async def create_hass() -> MockHomeAssistant:
    config_dir = Path(__file__).parent.parent / "homeassistant"
    hass = MockHomeAssistant(config_dir.absolute())
    loader.async_setup(hass)
    # TODO: Use safe mode, or some other way to disable I/O components?
    config_dict = await conf_util.async_hass_config_yaml(hass)
    await bootstrap.async_from_config_dict(config_dict, hass)
    return hass


@pytest_asyncio.fixture
async def hass() -> AsyncGenerator[MockHomeAssistant]:
    hass = await create_hass()
    await hass.async_start()
    yield hass
    await hass.check_assertions()

    await hass.async_stop()