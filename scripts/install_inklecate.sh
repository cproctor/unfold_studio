#!/usr/bin/env bash
# Downloads and extracts the inklecate compiler for the version specified in base_settings.py.
# Run from the repo root: bash scripts/install_inklecate.sh
# Requires: curl, unzip

set -euo pipefail

INK_VERSION="${INK_VERSION:-1.2.0}"
DEST_DIR="$(pwd)/inklecate_${INK_VERSION}"
GITHUB_BASE="https://github.com/inkle/ink/releases/download/v${INK_VERSION}"

if [[ "$(uname -s)" == "Darwin" ]]; then
    ARCHIVE="inklecate_mac.zip"
elif [[ "$(uname -s)" == "Linux" ]]; then
    ARCHIVE="inklecate_linux.zip"
else
    echo "Unsupported OS: $(uname -s)" >&2
    exit 1
fi

echo "Downloading inklecate ${INK_VERSION} (${ARCHIVE})..."
curl -fL "${GITHUB_BASE}/${ARCHIVE}" -o "/tmp/${ARCHIVE}"

echo "Extracting to ${DEST_DIR}..."
mkdir -p "${DEST_DIR}"
unzip -o "/tmp/${ARCHIVE}" -d "${DEST_DIR}"
chmod +x "${DEST_DIR}/inklecate"
rm "/tmp/${ARCHIVE}"

echo "Done. inklecate installed at ${DEST_DIR}/inklecate"
