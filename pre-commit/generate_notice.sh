#!/usr/bin/env bash
# shellcheck disable=SC1091
set -euo pipefail

APP_DIR=$(pwd)
IN_DOCKER=false

# Use to see if in container
if /opt/python/cp39-cp39/bin/python --version &>/dev/null; then
	IN_DOCKER=true
fi

if [ "$IN_DOCKER" = "false" ]; then

	if ! docker info &>/dev/null; then
		echo 'Please ensure Docker is installed and running on your machine'
		exit 1
	fi

	IMAGE="quay.io/pypa/manylinux_2_28_x86_64"
	script_name=$(basename "$0")

	# Run this script inside a manylinux Docker container
	exec docker run \
		--rm \
		-v "$APP_DIR":/src \
		-v "$(dirname "$0")":/srv/ \
		-w /src \
		"$IMAGE" \
		/bin/bash -c "/srv/$script_name"
fi

app_json="$(find ./*.json ! -name '*.postman_collection.json' | head -n 1)"

# Get the "name" and "license" keys from the JSON file, without having to install jq to do it
app_name=$(grep -oP '"name"\s*:\s*"\K[^"]+' "$app_json" | head -1)
app_license=$(grep -oP '"license"\s*:\s*"\K[^"]+' "$app_json")

{
	echo "Splunk SOAR App: $app_name"
	echo "$app_license"
} >"$APP_DIR"/NOTICE

if [ -s "$APP_DIR"/requirements.txt ]; then
	{
		echo ""
		echo "Third Party Software Attributions:"
		echo "----------------------------------"
		echo ""
	} >>"$APP_DIR"/NOTICE
else
	echo "Nothing in requirements.txt, all done."
	exit 0
fi

# Since we're running this in an ephemeral container, we don't care about caches or venvs
export PATH="/opt/python/cp39-cp39/bin:$PATH"
pip install \
	--no-cache-dir \
	--root-user-action ignore \
	pip-licenses \
	-r requirements.txt \
	>/dev/null
pip-licenses \
	--format=plain-vertical \
	--with-authors \
	--with-urls \
	--with-license-file \
	--with-notice-file \
	--no-license-path \
	2>/dev/null >>"$APP_DIR"/NOTICE

# Remove lines containing only the string "UNKNOWN"
sed -i '/^UNKNOWN$/d' "$APP_DIR"/NOTICE
