from homeassistant.core import HomeAssistant
from typing import Optional, List
from mockhass.assertion import BaseAssertion, EntityAssertion
import asyncio

class MockHomeAssistant(HomeAssistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assertions: List[BaseAssertion] = []

    def assert_entity(self, entity_id: str, *, attribute: Optional[str] = None, expected: Optional[str] = None) -> EntityAssertion:
        assertion = EntityAssertion(entity_id)
        if attribute is not None:
            assertion.attribute(attribute)
        if expected is not None:
            assertion.equals(expected)
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
        # Give templates a chance to update by waiting a short time
        # and then ensuring all tasks are done
        await asyncio.sleep(0.01)  # Small delay to allow listeners to fire
        await self.async_block_till_done()
        
        # Additional loop to catch any cascading updates
        for _ in range(3):
            await asyncio.sleep(0.01)
            await self.async_block_till_done()