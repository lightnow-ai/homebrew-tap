#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/sha256.sh <artifact-url>" >&2
  exit 2
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL "$1" -o "$tmp"
shasum -a 256 "$tmp" | awk '{print $1}'
