import pytest
from mockhass import MockHomeAssistant

@pytest.mark.asyncio
async def test_instantaneous_power_usage(hass: MockHomeAssistant):
    hass.states.async_set("climate.living_room_baseboard_heat", "off", {})
    hass.states.async_set("climate.kitchen_baseboard_heat", "off", {})
    hass.states.async_set("climate.dining_room_heat", "off", {})
    hass.states.async_set("climate.play_room_heat", "off", {})
    await hass.async_wait_for_template_updates()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.dining_room_radiant_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.play_room_baseboard_heat_estimated_power_usage").equals("0")
    await hass.check_assertions()

    hass.states.async_set("climate.living_room_baseboard_heat", "heat", {"hvac_action": "heating"})
    hass.states.async_set("climate.kitchen_baseboard_heat", "heat", {"hvac_action": "heating"})
    hass.states.async_set("climate.dining_room_heat", "heat", {"hvac_action": "heating"})
    hass.states.async_set("climate.play_room_heat", "heat", {"hvac_action": "heating"})
    await hass.async_wait_for_template_updates()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("1500")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("1000")
    hass.assert_entity("sensor.dining_room_radiant_heat_estimated_power_usage").equals("1000")
    hass.assert_entity("sensor.play_room_baseboard_heat_estimated_power_usage").equals("1000")
    await hass.check_assertions()

    hass.states.async_set("climate.living_room_baseboard_heat", "off", {"hvac_action": "off"})
    hass.states.async_set("climate.kitchen_baseboard_heat", "off", {"hvac_action": "off"})
    hass.states.async_set("climate.dining_room_heat", "off", {"hvac_action": "off"})
    hass.states.async_set("climate.play_room_heat", "off", {"hvac_action": "off"})
    await hass.async_wait_for_template_updates()
    hass.assert_entity("sensor.living_room_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.dining_room_radiant_heat_estimated_power_usage").equals("0")
    hass.assert_entity("sensor.play_room_baseboard_heat_estimated_power_usage").equals("0")
    await hass.check_assertions()