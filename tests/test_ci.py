"""Test continuous integration."""

from mockhass import MockHomeAssistant
from homeassistant.core import Service, SupportsResponse
from homeassistant.setup import async_setup_component
import pytest
from unittest.mock import MagicMock
import asyncio
from aiohttp import web, http_parser

class ServicePatch:
    def __init__(self, hass, monkeypatch):
        self.hass: MockHomeAssistant = hass
        self.monkeypatch: pytest.MonkeyPatch = monkeypatch

    async def patch(self, service, function = None, supports_response = False):
        if function is None:
            function = MagicMock()
            function.return_value = None
        if not service or "." not in service:
            raise ValueError("Invalid service in test setup")
        domain, service_name = service.split(".")
        domains = self.hass.services.async_services_internal()
        domain_services = domains.setdefault(domain, {})
        self.monkeypatch.setitem(domain_services, service_name, Service(
            schema=None,
            func=function,
            domain=domain,
            service=service_name,
            supports_response=SupportsResponse.OPTIONAL if supports_response else None
        ))
        return function


@pytest.fixture
def patch_service(hass, monkeypatch):
    """Monkeypatch a Home Assistant action for the duration of a test."""
    service_patch = ServicePatch(hass, monkeypatch)
    yield service_patch.patch
    service_patch.monkeypatch.undo()



@pytest.mark.skip("this test still needs work")
@pytest.mark.asyncio
async def test_ci_automation(hass: MockHomeAssistant, patch_service):
    """Test continuous integration automation."""
    mock_shell_command = MagicMock()
    mock_shell_command.return_value = {"returncode": 0}
    await async_setup_component(hass, "automation", {})
    await async_setup_component(hass, "webhook", {})
    await async_setup_component(hass, "http", {})
    await hass.async_block_till_done()
    shell_call = await patch_service("shell_command.update_home_assistant_config", mock_shell_command)
    restart = await patch_service("homeassistant.reload_all")

    # Grab webhook key from the automation -- super hacky
    # TODO: There's gotta be a better way to do this
    automation = hass.data['automation'].entities.mapping['automation.update_home_assistant_config']
    webhook_key = automation.raw_config['triggers'][0]['webhook_id']

    # Trigger the automation
    # TODO: Use a mock client instead
    request = MagicMock()
    request.headers = {"Content-Type": "application/json"}
    request.json.return_value = {"presigned_url": ""}
    request.query = {}
    
    print(hass.data['webhook'])
    await hass.data['webhook']['handler'](hass, webhook_key, request)

    # Check that the shell command was called
    assert shell_call.called
    service_data = shell_call.call_args[0][1]





    