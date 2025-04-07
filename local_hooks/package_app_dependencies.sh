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

# Remove any existing wheels in wheels/ and app json
yum install jq
if ! jq --help &>/dev/null; then
	echo 'Please ensure jq is installed (eg, brew install jq)'
	exit 1
fi
app_json="$(find ./*.json ! -name '*.postman_collection.json' | head -n 1)"
jq --indent 4 'del(.pip_dependencies) | del(.pip3_dependencies) | del(.pip36_dependencies) | del(.pip39_dependencies)' "$app_json" >tmp.json
mv tmp.json "$app_json"
rm -rf wheels

# Sanity check: We can import local_hooks, right?
python -c 'import local_hooks'

py39_deps='pip39_dependencies'
py313_deps='pip313_dependencies'
SCRIPT="python -m local_hooks.package_app_dependencies"

pip3.9 install pip-tools
${SCRIPT} . "$(which pip3.9)" "$py39_deps" --repair-wheels

pip3.13 install pip-tools
${SCRIPT} . "$(which pip3.13)" "$py313_deps" --repair-wheels

exit $?
