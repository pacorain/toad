#!/bin/sh

set -e

hass_config_dir="/config"

# Install openssl and rsync if not installed
# This assumes using Hass OS or Home Assistant Supervised
apk add --no-cache openssl rsync

# Get a temp dir to store the downloaded config file
tmp_dir=$(mktemp -d)

url=$1
encryption_key="{{ op://$HASS_VAULT_ID/config_encryption_key/password }}"
if [ -n "$2"]; then
    skip_check="1"
else
    skip_check=""
fi

# Pull and decrypt the config file
mkdir -p ${tmp_dir}/config
curl -s -o ${tmp_dir}/config.tar.gz.enc ${url}
openssl enc -d -aes-256-cbc -in ${tmp_dir}/config.tar.gz.enc -k "${encryption_key}" | tar -xz -C ${tmp_dir}/config

# Use rsync with --dry-run to count the number of files that would be changed
threshold=10

if [ -z "$skip_check" ]; then
    changed_files=$(rsync -av --dry-run ${tmp_dir}/config/homeassistant /config | grep -c '^homeassistant/')
    if [ "$changed_files" -gt "$threshold" ]; then
        echo "WARNING: More than $threshold files have changed. Aborting."
        exit 2
    fi
fi

# Sync the files
rsync -av ${tmp_dir}/config/homeassistant/ ${hass_config_dir}/