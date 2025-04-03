#!/usr/bin/env bash
set -euo pipefail

APP_DIR=$(pwd)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

IN_DOCKER=false

# Use to see if in container
if /opt/python/cp39-cp39/bin/python --version &>/dev/null; then
	IN_DOCKER=true
fi

app_json="$(find ./*.json ! -name '*.postman_collection.json' | head -n 1)"
pip3_dependencies="$(jq .pip3_dependencies "$app_json")"
if [[ $pip3_dependencies == 'null' ]]; then
	pip3_dependencies_key='pip_dependencies'
else
	pip3_dependencies_key='pip3_dependencies'
fi

pip39_dependencies_key='pip39_dependencies'
pip313_dependencies_key='pip313_dependencies'

if [ "$IN_DOCKER" = true ]; then
	/opt/python/cp39-cp39/bin/pip install pip-tools
	/opt/python/cp39-cp39/bin/python "$SCRIPT_DIR"/package_app_dependencies.py \
		. "/opt/python/cp39-cp39/bin/pip" "$pip3_dependencies_key" --repair_wheels
	/opt/python/cp39-cp39/bin/python "$SCRIPT_DIR"/package_app_dependencies.py \
		. "/opt/python/cp39-cp39/bin/pip" "$pip39_dependencies_key" --repair_wheels
	/opt/python/cp313-cp313/bin/pip install pip-tools
	/opt/python/cp313-cp313/bin/python "$SCRIPT_DIR"/package_app_dependencies.py \
		. "/opt/python/cp313-cp313/bin/pip" "$pip313_dependencies_key" --repair_wheels
	exit $?
fi

# Not in container, proceed with Docker setup
IMAGE="quay.io/pypa/manylinux_2_28_x86_64"
DOCKERFILE=""

while getopts 'i:d:' flag; do
	case "${flag}" in
	i) IMAGE="${OPTARG}" ;;
	d) DOCKERFILE="${OPTARG}" ;;
	*) echo "Invalid flag ${OPTARG}" && exit 1 ;;
	esac
done

function prepare_docker_image() {
	if [[ $DOCKERFILE != "" ]]; then
		local appdir_base
		local appdir_dir

		appdir_base=$(basename "$APP_DIR")
		appdir_dir=$(dirname "$APP_DIR")
		IMAGE=$(basename "$appdir_dir")/"$appdir_base"

		echo "Creating image from context $DOCKERFILE, tag: $IMAGE"
		docker build -t "$IMAGE" -f "$DOCKERFILE" "$APP_DIR"
	fi
	echo "Using image: $IMAGE"
}

function package_py3_app_dependencies() {
	PYTHON_VERSION_STRING=$1
	PIP_DEPENDENCIES_KEY=$2
	docker run --rm -v "$APP_DIR":/src -v "$SCRIPT_DIR":/local-hooks/ -w "$SCRIPT_DIR" \
		"$IMAGE" /bin/bash -c \
		"/opt/python/cp39-cp39/bin/python /local-hooks/package_app_dependencies.py \
     /src /opt/python/$PYTHON_VERSION_STRING/bin/pip $PIP_DEPENDENCIES_KEY --repair_wheels"
}

function package_py39_app_dependencies() {
	PYTHON_VERSION_STRING=$1
	PIP_DEPENDENCIES_KEY=$2
	docker run --rm -v "$APP_DIR":/src -v "$SCRIPT_DIR":/local-hooks/ -w "$SCRIPT_DIR" \
		"$IMAGE" /bin/bash -c \
		"/opt/python/cp39-cp39/bin/python /local-hooks/package_app_dependencies.py \
     /src /opt/python/$PYTHON_VERSION_STRING/bin/pip $PIP_DEPENDENCIES_KEY --repair_wheels"
}

function package_py313_app_dependencies() {
	PYTHON_VERSION_STRING=$1
	PIP_DEPENDENCIES_KEY=$2
	docker run --rm -v "$APP_DIR":/src -v "$SCRIPT_DIR":/local-hooks/ -w "$SCRIPT_DIR" \
		"$IMAGE" /bin/bash -c \
		"/opt/python/cp313-cp313/bin/python /local-hooks/package_app_dependencies.py \
     /src /opt/python/$PYTHON_VERSION_STRING/bin/pip $PIP_DEPENDENCIES_KEY --repair_wheels"
}

if ! docker info &>/dev/null; then
	echo 'Please ensure Docker is installed and running on your machine'
	exit 1
fi

prepare_docker_image
package_py3_app_dependencies 'cp36-cp36m' $pip3_dependencies_key
package_py39_app_dependencies 'cp39-cp39' $pip39_dependencies_key
package_py313_app_dependencies 'cp313-cp313' $pip313_dependencies_key
