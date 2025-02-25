from homeassistant.core import HomeAssistant


class BaseAssertion:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def check(self):
        raise NotImplementedError()


class EntityAssertion(BaseAssertion):
    def __init__(self, entity_id: str, hass: HomeAssistant):
        super().__init__(hass)
        self.entity_id = entity_id
        self.attribute = None
        self.value_to_check = None
        self.fn = None
        # TODO: Set to False if something has changed?
        self.checked = False

    def attribute(self, attribute: str):
        self.attribute = attribute
        return self

    def equals(self, expected: str):
        # TODO: Raise an error if fn or expected exists?
        self.fn = "equals"
        self.value_to_check = expected
        return self

    async def check(self):
        if self.checked:
            return True
        self.checked = True
        if self.fn is None:
            raise ValueError("No assertion function set")
        state = self.hass.states.get(self.entity_id)
        if state is None:
            raise AssertionError(f"Entity {self.entity_id} not found")
        if self.attribute is not None:
            value = state.attributes.get(self.attribute)
        else:
            value = state.state
        if self.fn == "equals":
            assert (
                value == self.value_to_check
            ), f"Expected entity {self.entity_id} to be {self.value_to_check}, but got {value}"
        else:
            raise ValueError(f"Unknown assertion function {self.fn}")
