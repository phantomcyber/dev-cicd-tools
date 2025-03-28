#!/usr/bin/env bash
set -euo pipefail

APP_DIR=$(pwd)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

IN_DOCKER=false

# Use to see if in container
if /opt/python/cp39-cp39/bin/python --version &>/dev/null; then
	IN_DOCKER=true
fi

if ! jq --help &>/dev/null; then
	echo 'Please ensure jq is installed (eg, brew install jq)'
	exit 1
fi

app_json="$(find ./*.json ! -name '*.postman_collection.json' | head -n 1)"
publisher=$(jq -r '.publisher' "$app_json")
if [[ $publisher == 'Splunk' ]]; then
	test_mode='splunk_supported'
else
	test_mode='developer_supported'
fi

if [ "$IN_DOCKER" = true ]; then
	/opt/python/cp39-cp39/bin/pip install jsonschema lxml 'django<5'
	/opt/python/cp39-cp39/bin/python "$SCRIPT_DIR"/static_tests.py "$test_mode" . --app-repo-name "$(basename "$APP_DIR")"
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

if ! docker info &>/dev/null; then
	echo 'Please ensure Docker is installed and running on your machine'
	exit 1
fi

prepare_docker_image
docker run --rm \
	--mount type=bind,source=/etc/localtime,target=/etc/localtime,readonly \
	-v "$APP_DIR":/src \
	-v "$SCRIPT_DIR":/pre-commit/ \
	-w /src \
	"$IMAGE" /bin/bash -c \
	"/opt/python/cp39-cp39/bin/pip install jsonschema lxml 'django<5' && \
     /opt/python/cp39-cp39/bin/python /pre-commit/static_tests.py $test_mode . --app-repo-name $(basename "$APP_DIR")"
