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
app_name=$(jq -r .name "$app_json")
app_license=$(jq -r .license "$app_json")

if [ "$IN_DOCKER" = true ]; then
	if [ ! -s "$APP_DIR"/requirements.txt ]; then
		echo "Nothing in requirements.txt, skipping NOTICE generation"
		exit 0
	fi
	if grep -q "Third Party Software Attributions:" "$APP_DIR"/NOTICE; then
		echo "NOTICE has already been updated, skipping NOTICE generation"
		exit 0
	fi
	{
		echo "Splunk SOAR $app_name"
		echo "$app_license"
		echo ""
		echo "Third Party Software Attributions:"
		echo ""
	} >"$APP_DIR"/NOTICE
	/opt/python/cp39-cp39/bin/python -m venv "$APP_DIR"/venv
	source "$APP_DIR"/venv/bin/activate
	"$APP_DIR"/venv/bin/pip install -r requirements.txt
	# shellcheck disable=SC2046
	"$APP_DIR"/venv/bin/pip show $(pip freeze | cut -d= -f1) | grep -E 'Name:|Author:|Version:|License:|Maintainer:' >>"$APP_DIR"/NOTICE
	# shellcheck disable=SC1003
	sed -i '/License:/a\'$'\n' "$APP_DIR"/NOTICE
	deactivate
	rm -rf "$APP_DIR"/venv
	exit 0
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
	docker run --rm -v "$APP_DIR":/src "$IMAGE" /bin/bash -c -w /src \
		"app_json=\$(find /src/*.json ! -name '*.postman_collection.json' | head -n 1) &&
        app_name=\$(jq -r .name \$app_json) &&
        app_license=\$(jq -r .license \$app_json) &&
		if [ ! -s /src/requirements.txt ]; then
			echo 'Nothing in requirements.txt, skipping NOTICE generation'
			exit 0
		fi &&
		if grep -q 'Third Party Software Attributions:' src/NOTICE; then
			echo 'NOTICE has already been updated, skipping NOTICE generation'
			exit 0
		fi &&
		{
			echo 'Splunk SOAR $app_name'
			echo '$app_license'
			echo ''
			echo 'Third Party Software Attributions:'
			echo ''
		} >'$APP_DIR'/NOTICE &&
        /opt/python/cp39-cp39/bin/python -m venv /src/venv &&
        source /src/venv/bin/activate &&
        /src/venv/bin/pip install --force-reinstall -r requirements.txt &&
        '$APP_DIR'/venv/bin/pip show $(pip freeze | cut -d= -f1) | grep -E 'Name:|Author:|Version:|License:|Maintainer:' >>'$APP_DIR'/NOTICE &&
		deactivate &&
        rm -rf /src/venv"
}

if ! docker info &>/dev/null; then
	echo 'Please ensure Docker is installed and running on your machine'
	exit 1
fi

prepare_docker_image
generate_notice
