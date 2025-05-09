#!/usr/bin/env bash
set -euo pipefail

APP_DIR=$(pwd)
PY39_BIN="/opt/python/cp39-cp39/bin"
PY313_BIN="/opt/python/cp313-cp313/bin"

# If we're not in a docker container, push ourselves into one and execute the script there
if ! "${PY39_BIN}/python" --version &>/dev/null; then
	if ! docker info &>/dev/null; then
		echo 'Please ensure Docker is installed and running on your machine'
		exit 1
	fi

	IMAGE="quay.io/pypa/manylinux_2_28_x86_64"
	script_name=$(basename "$0")
	PY_SITE=$(python -c 'import site; print(site.getsitepackages()[0])')

	# Run this script inside a manylinux Docker container
	exec docker run \
		--rm \
		-v "$APP_DIR":/src \
		-v "$(dirname "$0")":/srv/ \
		-v "$PY_SITE":/site-packages \
		-e "PYTHONPATH=/site-packages" \
		-w /src \
		"$IMAGE" \
		/bin/bash -c "/srv/$script_name"
fi

export PATH="$PY39_BIN:$PY313_BIN:$PATH"

# Sanity check: We can import local_hooks, right? If not, it's probably because we were already
# running in a docker container and we didn't volume mount the site-packages directory
# If that's the case, try to import local_hooks from pre-commit Python's site-packages
if ! python -c 'import local_hooks'; then
	#shellcheck disable=SC2034,SC2046
	PYTHONPATH="$($(dirname "$0")/python -c 'import site; print(site.getsitepackages()[0])')"
	export PYTHONPATH
	echo "$PYTHONPATH"
	python -c 'import local_hooks'
fi

# Remove any existing wheels in wheels/ and app json
yum install jq -y
if ! jq --help &>/dev/null; then
	echo 'Something went wrong installing jq. Could not find it on PATH after installation. Aborting'
	exit 1
fi

py39_deps='pip39_dependencies'
py313_deps='pip313_dependencies'
SCRIPT="python -m local_hooks.package_app_dependencies"

pip3.9 install pip-tools
${SCRIPT} . "$(which pip3.9)" "$py39_deps" --repair-wheels

pip3.13 install pip-tools
${SCRIPT} . "$(which pip3.13)" "$py313_deps" --repair-wheels

exit $?
