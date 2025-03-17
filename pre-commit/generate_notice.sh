#!/usr/bin/env bash
# shellcheck disable=SC1091
set -euo pipefail

APP_DIR=$(pwd)
IN_DOCKER=false

# Use to see if in container
if /opt/python/cp39-cp39/bin/python --version &>/dev/null; then
	IN_DOCKER=true
fi

app_json="$(find ./*.json ! -name '*.postman_collection.json' | head -n 1)"
app_py_version="$(jq .python_version "$app_json")"
if [[ $app_py_version == 'null' ]]; then
	app_py_version='"2.7"'
fi

if [[ $app_py_version == '"2.7"' ]]; then
	echo "Python 2 is no longer supported"
	exit 1
fi

if [ "$IN_DOCKER" = true ]; then
	/opt/python/cp39-cp39/bin/python -m venv "$APP_DIR"/notice_venv
	source "$APP_DIR"/notice_venv/bin/activate
	/opt/python/cp39-cp39/bin/pip install pip-licenses
	pip-licenses --from=mixed --format=markdown --with-license-file --no-license-path --with-maintainers --order=license -n >>"$APP_DIR"/NOTICE
	deactivate
	rm -rf "$APP_DIR"/notice_venv
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

function generate_notice() {
	docker run --rm -v "$APP_DIR":/src "$IMAGE" /bin/bash -c \
		"set -e && /opt/python/cp39-cp39/bin/python -m venv /src/notice_venv && ls -lath && source /src/notice_venv/bin/activate &&
		/opt/python/cp39-cp39/bin/pip install pip-licenses && /opt/python/cp39-cp39/bin/pip install -r requirements.txt &&
		pip-licenses --from=mixed --format=markdown --with-license-file --no-license-path --with-maintainers --order=license -n >> /src/NOTICE &&
		deactivate && rm -rf /src/notice_venv"
}

if ! docker info &>/dev/null; then
	echo 'Please ensure Docker is installed and running on your machine'
	exit 1
fi

prepare_docker_image
generate_notice
