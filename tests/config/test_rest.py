def test_rest_integrations_have_user_agent_header(compiled_config):
    """Test that all REST integrations have a User-Agent header
    
    When querying external services, I want to be clear that the request is coming from an automated system.
    """
    for domain, config in compiled_config.items():
        if domain == "rest":
            for rest_config in config:
                headers = rest_config.get("headers")
                assert headers is not None, "Missing headers"
                assert "User-Agent" in headers, "Missing User-Agent"
        elif domain == "rest_command":
            for name, rest_config in config.items():
                headers = rest_config.get("headers")
                assert headers is not None, f"Missing headers in {domain} {name}"
                assert "User-Agent" in headers, f"Missing User-Agent in {domain} {name}"
        elif domain.startswith("rest"):
            raise ValueError(f"Unhandled RESTful domain {domain} -- please update test")
        