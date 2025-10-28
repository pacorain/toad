import pytest
from mockhass import MockHomeAssistant

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Testing framework is not working correctly")
async def test_instantaneous_power_usage(hass: MockHomeAssistant):
    hass.states.async_set("climate.living_room_baseboard_heat", "off", {})
    hass.states.async_set("climate.kitchen_baseboard_heat", "off", {})
    await hass.async_block_till_done()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("0")

    hass.states.async_set("climate.living_room_baseboard_heat", "heat", {"hvac_action": "heating"})
    hass.states.async_set("climate.kitchen_baseboard_heat", "heat", {"hvac_action": "heating"})
    await hass.async_block_till_done()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("1500")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("1000")

    hass.states.async_set("climate.living_room_baseboard_heat", "off", {"hvac_action": "off"})
    hass.states.async_set("climate.kitchen_baseboard_heat", "off", {"hvac_action": "off"})
    await hass.async_block_till_done()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("0")