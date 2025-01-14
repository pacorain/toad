# Toad - Smart Home Config

v3 of my Smart Home Config

---

# Components

- [Testing](#testing) - Unit tests and convention enforcement for config changes

...more to come as I build out the config.

# Testing

I've started writing a **framework for testing my Smart Home Config**. This is helpful for me to make sure that my home automation behaves as expected, especially with complex scenarios (i.e. automations that behave differently if we have guests) or critical components (like home security).

The framework works by creating a mock Home Assistant instance with this repo as a config. The tests are expected to emulate devices and changes to the home, and assert that the config responds in a certain way.

The framework itself currently lives in [src/python/mockhass](), and the tests live in [tests]().