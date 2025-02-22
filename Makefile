TEMPLATES := $(shell git ls-files '*.tpl')
TARGETS := $(TEMPLATES:.tpl=)
HASS_VAULT_ID := "Home Assistant"

.PHONY: secrets $(TARGETS)

secrets: $(TARGETS)

$(TARGETS):
	HASS_VAULT_ID=$(HASS_VAULT_ID) op inject -f -i $@.tpl -o $@