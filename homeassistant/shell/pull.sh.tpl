#!/bin/sh

set -e

local hass_config_dir="/config"

# Get a temp dir to store the downloaded config file
local tmp_dir=$(mktemp -d)

local url=$1
local encryption_key="{{ op://$HASS_VAULT_ID/config_encryption_key/value }}"
if [ -n "$2"]; then
    local skip_check="1"
else
    local skip_check=""
fi

# Pull and decrypt the config file
curl -s -o ${tmp_dir}/config.tar.gz.enc ${url}
openssl enc -d -aes-256-cbc -in ${tmp_dir}/config.tar.gz.enc -k ${encryption_key} | tar -xz -C ${tmp_dir}/config

# Use rsync with --dry-run to count the number of files that would be changed
threshold=10

if [ -z "$skip_check" ]; then
    local changed_files=$(rsync -av --dry-run ${tmp_dir}/config/ /config | grep -c '^>f')
    if [ "$changed_files" -gt "$threshold" ]; then
        echo "WARNING: More than $threshold files have changed. Aborting."
        exit 2
    fi
fi

# Sync the files
rsync -av ${tmp_dir}/config/ ${hass_config_dir}