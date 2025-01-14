from homeassistant.core import HomeAssistant
from typing import Optional, List
from mockhass.assertion import BaseAssertion, EntityAssertion

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