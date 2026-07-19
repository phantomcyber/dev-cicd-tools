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

HOOKS_PYTHONPATH="${PYTHONPATH:-}"

# Sanity check: We can import local_hooks, right? If not, it's probably because we were already
# running in a docker container and we didn't volume mount the site-packages directory
# If that's the case, try to import local_hooks from pre-commit Python's site-packages
if ! python -c 'import local_hooks'; then
	#shellcheck disable=SC2034,SC2046
	HOOKS_PYTHONPATH="$($(dirname "$0")/python -c 'import site; print(site.getsitepackages()[0])')"
	export PYTHONPATH="$HOOKS_PYTHONPATH"
	python -c 'import local_hooks'
fi

# The mounted pre-commit site-packages may contain host pip code from a newer Python version.
# Limit that path to local_hooks imports so container pip3.9/pip3.13 use their own interpreter-local pip.
unset PYTHONPATH

py39_deps='pip39_dependencies'
py313_deps='pip313_dependencies'
SCRIPT="python -m local_hooks.package_app_dependencies"

# Restore the hook import path only for the packager itself; child pip processes clear it again.
run_packager() {
	if [[ -n "${HOOKS_PYTHONPATH:-}" ]]; then
		PYTHONPATH="$HOOKS_PYTHONPATH" ${SCRIPT} "$@"
	else
		${SCRIPT} "$@"
	fi
}

has_pip_dependency_key() {
	local dependency_key="$1"
	local check_dependency_key
	check_dependency_key='from local_hooks.package_app_dependencies import _should_package_pip_dependency_key; import sys; sys.exit(not _should_package_pip_dependency_key(".", sys.argv[1]))'

	if [[ -n "${HOOKS_PYTHONPATH:-}" ]]; then
		PYTHONPATH="$HOOKS_PYTHONPATH" python -c "$check_dependency_key" "$dependency_key"
	else
		python -c "$check_dependency_key" "$dependency_key"
	fi
}

package_dependencies() {
	local dependency_key="$1"
	local pip_path="$2"

	if ! has_pip_dependency_key "$dependency_key"; then
		echo "Skipping $dependency_key because it is not declared in the app manifest"
		return
	fi

	env -u PYTHONPATH "$pip_path" install pip-tools
	run_packager . "$pip_path" "$dependency_key" --repair-wheels
}

package_dependencies "$py39_deps" "$(which pip3.9)"
package_dependencies "$py313_deps" "$(which pip3.13)"

exit $?
