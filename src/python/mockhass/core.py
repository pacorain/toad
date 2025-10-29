from homeassistant.core import HomeAssistant
from typing import Optional, List
from mockhass.assertion import BaseAssertion, EntityAssertion
import asyncio
import datetime
from freezegun import freeze_time
from freezegun.api import FrozenDateTimeFactory
from unittest.mock import patch, MagicMock

class MockHomeAssistant(HomeAssistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assertions: List[BaseAssertion] = []
        self._time_frozen: bool = False
        self._freezer: Optional[FrozenDateTimeFactory] = None
        self._time_patches: List = []
        self._base_time: Optional[datetime.datetime] = None

    def assert_entity(self, entity_id: str, *, attribute: Optional[str] = None, expected: Optional[str] = None) -> EntityAssertion:
        assertion = EntityAssertion(entity_id)
        if attribute is not None:
            assertion.attribute(attribute)
        # Note: if expected is provided, the user must await equals() themselves
        self.assertions.append(assertion)
        return assertion
    
    async def check_assertions(self):
        for assertion in self.assertions:
            await assertion.check(self)
        self.assertions = []
    
    async def async_wait_for_template_updates(self, timeout: float = 1.0):
        """
        Wait for template sensors and other reactive entities to update after state changes.
        
        This is needed because template sensors update asynchronously via event listeners,
        and async_block_till_done() may not wait for those updates to complete.
        
        Args:
            timeout: Maximum time to wait for updates (default: 1.0 seconds)
        """
        # If time is frozen, we need to be careful with asyncio.sleep
        # Use a small real delay to allow event loop to process
        if self._time_frozen:
            # When time is frozen, asyncio.sleep might not work correctly
            # Instead, yield control to the event loop using asyncio.sleep(0)
            await asyncio.sleep(0)
            await self.async_block_till_done()
            
            # Additional cycles without blocking sleeps
            for _ in range(3):
                await asyncio.sleep(0)  # Yield to event loop
                await self.async_block_till_done()
        else:
            # Normal operation: use small real sleeps
            await asyncio.sleep(0.01)  # Small delay to allow listeners to fire
            await self.async_block_till_done()
            
            # Additional loop to catch any cascading updates
            for _ in range(3):
                await asyncio.sleep(0.01)
                await self.async_block_till_done()
    
    def _start_time_mocking(self, start_time: Optional[datetime.datetime] = None):
        """
        Start mocking time. This should be called before using fast_forward().
        
        Args:
            start_time: Optional datetime to start from. Defaults to current time if None.
        """
        if self._time_frozen:
            return  # Already frozen
        
        if start_time is None:
            start_time = datetime.datetime.now(datetime.timezone.utc)
        
        self._base_time = start_time
        self._freezer = freeze_time(start_time)
        self._freezer.start()
        
        # Patch Home Assistant's time utilities
        # These are the main functions used by integration sensors and utility meters
        from homeassistant.util import dt as dt_util
        
        # Patch utcnow and now from homeassistant.util.dt
        # We need to create wrapper functions that return the current frozen time
        def get_frozen_utcnow():
            # Get the current frozen time from datetime (freezegun intercepts it)
            return datetime.datetime.now(datetime.timezone.utc)
        
        def get_frozen_now(tz=None):
            # Get the current frozen time with timezone
            if tz is None:
                tz = datetime.timezone.utc
            return datetime.datetime.now(tz)
        
        utcnow_patch = patch.object(dt_util, 'utcnow', side_effect=get_frozen_utcnow)
        now_patch = patch.object(dt_util, 'now', side_effect=get_frozen_now)
        
        utcnow_patch.start()
        now_patch.start()
        
        self._time_patches = [utcnow_patch, now_patch]
        self._time_frozen = True
        
        # Patch asyncio event loop time if available
        # This helps with any time-based async operations
        # Only patch if loop is available (might not be during initialization)
        try:
            loop = getattr(self, 'loop', None)
            if loop is not None and hasattr(loop, 'time'):
                original_time = loop.time
                base_loop_time = original_time()
                frozen_epoch = start_time.timestamp()
                
                def mock_loop_time():
                    if self._freezer is not None:
                        current_frozen = self._freezer.time_to_freeze.timestamp()
                        elapsed = current_frozen - frozen_epoch
                        return base_loop_time + elapsed
                    return original_time()
                
                loop_time_patch = patch.object(loop, 'time', side_effect=mock_loop_time)
                loop_time_patch.start()
                self._time_patches.append(loop_time_patch)
        except (AttributeError, RuntimeError):
            # Loop might not be available yet, that's okay
            # We'll skip loop time patching in this case
            pass
    
    async def fast_forward(
        self,
        seconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        days: float = 0
    ):
        """
        Fast forward time by the specified duration. Time will be frozen automatically if needed.
        
        This will advance the mocked time and trigger any time-dependent sensor updates.
        
        Args:
            seconds: Number of seconds to advance
            minutes: Number of minutes to advance
            hours: Number of hours to advance
            days: Number of days to advance
        """
        # Automatically freeze time if not already frozen
        if not self._time_frozen or self._freezer is None:
            self.freeze_time()
        
        total_seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 86400)
        
        if total_seconds <= 0:
            return
        
        # Advance the freezer time
        # Freezegun doesn't have a tick() method - we need to stop and restart with new time
        current_frozen_time = datetime.datetime.now(datetime.timezone.utc)
        new_time = current_frozen_time + datetime.timedelta(seconds=total_seconds)
        
        # Stop current freezer and create a new one with the advanced time
        self._freezer.stop()
        self._freezer = freeze_time(new_time)
        self._freezer.start()
        
        # Update the patches to use the new freezer time
        from homeassistant.util import dt as dt_util
        
        # Restart the patches with updated functions
        for patch_obj in self._time_patches[:2]:  # Only the dt_util patches
            patch_obj.stop()
        
        def get_frozen_utcnow():
            return datetime.datetime.now(datetime.timezone.utc)
        
        def get_frozen_now(tz=None):
            if tz is None:
                tz = datetime.timezone.utc
            return datetime.datetime.now(tz)
        
        utcnow_patch = patch.object(dt_util, 'utcnow', side_effect=get_frozen_utcnow)
        now_patch = patch.object(dt_util, 'now', side_effect=get_frozen_now)
        
        utcnow_patch.start()
        now_patch.start()
        
        self._time_patches = [utcnow_patch, now_patch] + self._time_patches[2:]  # Keep loop patch if exists
        
        # Integration sensors update when their source sensor states change.
        # To force integration sensors to recalculate after time advances,
        # we need to trigger state change events on source sensors.
        # Integration sensors listen to these events and will detect the time difference.
        
        from homeassistant.const import EVENT_STATE_CHANGED
        
        # Trigger state change events for all current sensor states
        # This causes integration sensors to recalculate using the new time
        # We iterate through all states and re-fire state change events for sensors
        # This is a bit brute-force but ensures all integration sensors get a chance to update
        for entity in list(self.states.async_all()):
            if entity.entity_id.startswith("sensor."):
                # Re-fire state change to trigger integration sensor updates
                # Integration sensors will see the state change and recalculate
                # based on the time difference since last update
                self.bus.async_fire(EVENT_STATE_CHANGED, {
                    "entity_id": entity.entity_id,
                    "old_state": entity,
                    "new_state": entity,
                })
        
        # Wait for integration sensors to process the time change
        await self.async_wait_for_template_updates()
        
        # Give additional cycles for integration sensors to fully recalculate
        # They may need multiple passes to update correctly
        # Use sleep(0) to yield to event loop without advancing time
        for _ in range(5):
            await asyncio.sleep(0)  # Yield to event loop to process updates
            await self.async_block_till_done()
    
    def freeze_time(self, freeze_time_str: Optional[str] = None):
        """
        Freeze time at a specific point. Should be called after hass.async_start()
        to avoid interfering with Home Assistant initialization.
        
        Args:
            freeze_time_str: Time to freeze at (ISO format string or None for current time)
        """
        if freeze_time_str:
            start_time = datetime.datetime.fromisoformat(freeze_time_str.replace('Z', '+00:00'))
        else:
            # Use a fixed time for consistency, but default to "now" if not specified
            start_time = datetime.datetime.now(datetime.timezone.utc)
        
        if self._time_frozen:
            # Stop existing freezer and patches
            self._stop_time_mocking()
        
        self._start_time_mocking(start_time)
    
    def _stop_time_mocking(self):
        """Stop time mocking and clean up patches."""
        if self._freezer is not None:
            self._freezer.stop()
            self._freezer = None
        
        for patch_obj in self._time_patches:
            patch_obj.stop()
        
        self._time_patches = []
        self._time_frozen = False
        self._base_time = None
    
    async def async_stop(self, *args, **kwargs):
        """Override async_stop to clean up time mocking."""
        self._stop_time_mocking()
        return await super().async_stop(*args, **kwargs)