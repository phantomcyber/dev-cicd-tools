#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if [ -z "$SEMGREP_DEPLOYMENT_ID" ] || [ -z "$SEMGREP_TOKEN" ]; then
	echo 'SEMGREP_DEPLOYMENT_ID and SEMGREP_TOKEN must be set'
	exit 1
fi

if ! docker &>/dev/null; then
	echo 'Please make sure Docker is installed and running'
	exit 1
fi

SEMGREP_IMAGE='returntocorp/semgrep-upload:latest'
docker pull "$SEMGREP_IMAGE"

cd "$SCRIPT_DIR"
find rules -path '**/*.yml' -or -path '**/*.yaml' | while read -r file; do
	echo "Uploading $file..."
	docker run -v "$(pwd)":/temp \
		-e SEMGREP_UPLOAD_DEPLOYMENT="$SEMGREP_DEPLOYMENT_ID" \
		-e SEMGREP_TOKEN="$SEMGREP_TOKEN" \
		"$SEMGREP_IMAGE" "/temp/$file"
done
