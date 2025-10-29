from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant

class BaseAssertion:
    async def check(self, hass: HomeAssistant):
        raise NotImplementedError()


class EntityAssertion(BaseAssertion):
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.attribute = None
        self.value_to_check = None
        self.tolerance = None
        self.fn = None
        self.checked = False

    def attribute(self, attribute: str):
        self.attribute = attribute
        return self
    
    def equals(self, expected: str):
        # Configure the assertion; actual checking happens in check()
        self.fn = "equals"
        self.value_to_check = expected
        return self
    
    def approximately(self, expected: float, tolerance: float = 0.01):
        """
        Assert that the entity value is approximately equal to the expected value.
        
        Args:
            expected: The expected numeric value
            tolerance: The maximum allowed difference (default: 0.01)
        
        Returns:
            self for method chaining
        """
        self.fn = "approximately"
        self.value_to_check = expected
        self.tolerance = tolerance
        return self

    async def check(self, hass: HomeAssistant):
        if self.checked:
            return True
        if self.fn is None:
            raise ValueError("No assertion function set")
        state = hass.states.get(self.entity_id)
        if state is None:
            raise AssertionError(f"Entity {self.entity_id} not found")
        if self.attribute is not None:
            value = state.attributes.get(self.attribute)
        else:
            value = state.state
        
        if self.fn == "equals":
            assert value == self.value_to_check, f"Expected entity {self.entity_id} to be {self.value_to_check}, but got {value}"
        elif self.fn == "approximately":
            # Convert values to float for numeric comparison
            try:
                actual_value = float(value)
                expected_value = float(self.value_to_check)
                tolerance = float(self.tolerance) if self.tolerance is not None else 0.01
            except (ValueError, TypeError) as e:
                raise AssertionError(
                    f"Cannot compare entity {self.entity_id} approximately: "
                    f"value '{value}' cannot be converted to float. Error: {e}"
                ) from e
            
            diff = abs(actual_value - expected_value)
            assert diff <= tolerance, (
                f"Expected entity {self.entity_id} to be approximately {expected_value} "
                f"(within ±{tolerance}), but got {actual_value} "
                f"(difference: {diff:.6f})"
            )
        else:
            raise ValueError(f"Unknown assertion function {self.fn}")
        self.checked = True