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


@pytest.mark.asyncio
async def test_utility_meter_power_usage(hass: MockHomeAssistant):
    """
    Test that turning on a heater for 2 hours results in the expected kWh usage.
    
    Kitchen baseboard heat is 1000W. Running for 2 hours should consume 2 kWh.
    """
    # Freeze time to enable time mocking
    # fast_forward() will auto-freeze, but it's better to freeze first for consistency
    # TODO: This may cause issues if the test is run within the last two hours of the 28th day of the month.
    # Update this to use a fixed time.
    hass.freeze_time()
    
    # Turn on the heater
    hass.states.async_set("climate.kitchen_baseboard_heat", "heat", {"hvac_action": "heating"})
    await hass.async_wait_for_template_updates()
    
    # Verify power usage is being tracked
    hass.assert_entity("sensor.kitchen_baseboard_heat_estimated_power_usage").equals("1000")
    await hass.check_assertions()
    
    # Fast forward 2 hours - the integration sensor should accumulate the power usage
    # Then turn off the heater to trigger the integration sensor to update
    # fast_forward() will automatically freeze time if not already frozen
    await hass.fast_forward(hours=2)
    hass.states.async_set("climate.kitchen_baseboard_heat", "off", {"hvac_action": "off"})
    await hass.async_wait_for_template_updates()
    
    # Verify the integration sensor shows approximately 2 kWh with some tolerance
    hass.assert_entity("sensor.kitchen_heat_power_usage").approximately(2.0, tolerance=0.1)
    hass.assert_entity("sensor.kitchen_heat_monthly_power_usage").approximately(2.0, tolerance=0.1)
    await hass.check_assertions()