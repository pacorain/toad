import pytest_asyncio
import pytest
from typing import AsyncGenerator
from mockhass import MockHomeAssistant
from homeassistant import loader, config as conf_util, bootstrap, config_entries
from homeassistant.helpers import entity
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.scripts.check_config import async_check_config
import asyncio
import functools as ft
from unittest.mock import Mock, AsyncMock
from homeassistant.util.async_ import create_eager_task
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "homeassistant"

async def create_hass() -> MockHomeAssistant:
    hass = MockHomeAssistant(CONFIG_DIR.absolute())
    loader.async_setup(hass)
    entity.async_setup(hass)

    hass.config.location_name = "test home"
    hass.config.latitude = 32.87336
    hass.config.longitude = -117.22743
    hass.config.elevation = 0
    await hass.config.async_set_time_zone("US/Pacific")
    hass.config.units = METRIC_SYSTEM
    hass.config.media_dirs = {"local": str(Path(__file__).parent.parent / "homeassistant" / "media")}
    hass.config.skip_pip = True
    hass.config.skip_pip_packages = []

    hass.config_entries = config_entries.ConfigEntries(hass, {"_": (
                "Not empty or else some bad checks for hass config in discovery.py"
                " breaks"
            )})

    # TODO: Use safe mode, or some other way to disable I/O components?
    config_dict = await conf_util.async_hass_config_yaml(hass)
    del config_dict["default_config"]
    config_dict.setdefault("http", {})
    await bootstrap.async_from_config_dict(config_dict, hass)
    return config_dict, hass


@pytest.fixture
async def hass() -> AsyncGenerator[MockHomeAssistant]:
    _, hass = await create_hass()
    await hass.async_start()
    yield hass
    await hass.check_assertions()

    loaded_entries = [
            entry
            for entry in hass.config_entries.async_entries()
            if entry.state is ConfigEntryState.LOADED
    ]
        
    if loaded_entries:
        await asyncio.gather(
            *(
                create_eager_task(
                    hass.config_entries.async_unload(config_entry.entry_id),
                    loop=hass.loop,
                )
                for config_entry in loaded_entries
            )
        )

    await hass.async_stop(force=True)
    await hass.async_block_till_done()

@pytest.fixture
async def compiled_config():
    config_dict, _ = await create_hass()
    print(config_dict)
    return config_dict