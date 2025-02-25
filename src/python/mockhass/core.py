from homeassistant.core import HomeAssistant
from typing import Optional, List
from mockhass.assertion import BaseAssertion, EntityAssertion

class MockHomeAssistant(HomeAssistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assertions: List[BaseAssertion] = []

    def assert_entity(self, entity_id: str, *, attribute: Optional[str] = None, expected: Optional[str] = None) -> EntityAssertion:
        assertion = EntityAssertion(entity_id, hass=self)
        if attribute is not None:
            assertion.attribute(attribute)
        if expected is not None:
            assertion.equals(expected)
        self.assertions.append(assertion)
        return assertion
    
    def has_assertions(self) -> bool:
        for assertion in self.assertions:
            if not assertion.checked:
                return True
        return False
    
    async def check_assertions(self):
        # TODO: Make this parallel with asyncio.gather
        for assertion in self.assertions:
            await assertion.check()
        self.assertions = []

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.check_assertions()
        return False