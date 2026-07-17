#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: scripts/update-formula.sh <lightnow-cli|lightnow-proxy> <version>" >&2
  exit 2
fi

formula="$1"
version="$2"

case "$formula" in
  lightnow-cli | lightnow-proxy)
    package="$formula"
    ;;
  *)
    echo "unsupported formula: $formula" >&2
    exit 2
    ;;
esac

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "invalid release version: $version" >&2
  exit 2
fi

read -r sdist_filename sdist_url sdist_sha256 < <(python3 - "$package" "$version" <<'PY'
import json
import sys
import urllib.error
import urllib.request

package, version = sys.argv[1:]
try:
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{package}/{version}/json", timeout=30
    ) as response:
        release = json.load(response)
except urllib.error.HTTPError as error:
    raise SystemExit(
        f"PyPI release is not available: {package} {version} (HTTP {error.code})"
    ) from error

sdists = [
    item
    for item in release["urls"]
    if item["packagetype"] == "sdist" and not item.get("yanked", False)
]
if len(sdists) != 1:
    raise SystemExit(
        f"expected exactly one non-yanked PyPI sdist for {package} {version}, found {len(sdists)}"
    )
sdist = sdists[0]
print(sdist["filename"], sdist["url"], sdist["digests"]["sha256"])
PY
)
echo "Verified PyPI sdist: $sdist_filename"

tap_name="${HOMEBREW_TAP_NAME:-lightnow-ai/tap}"
formula_ref="${tap_name}/${formula}"

read -r current_version current_url current_sha256 < <(
  brew info --json=v2 "$formula_ref" | python3 -c '
import json
import sys

formula = json.load(sys.stdin)["formulae"][0]
stable = formula["urls"]["stable"]
print(formula["versions"]["stable"], stable["url"], stable["checksum"])
'
)

version_order="$(python3 - "$current_version" "$version" <<'PY'
import sys

current = tuple(map(int, sys.argv[1].split(".")))
requested = tuple(map(int, sys.argv[2].split(".")))
print((current > requested) - (current < requested))
PY
)"

if [ "$version_order" -gt 0 ]; then
  echo "Ignoring stale update for $formula $version; formula is already $current_version."
  exit 0
fi

if [ "$version_order" -eq 0 ]; then
  if [ "$current_url" != "$sdist_url" ] || [ "$current_sha256" != "$sdist_sha256" ]; then
    echo "$formula $version has a URL or checksum that differs from PyPI" >&2
    exit 1
  fi
  echo "Formula already represents $formula $version."
  exit 0
fi

formula_path="$(git rev-parse --show-toplevel)/Formula/${formula}.rb"
python3 - \
  "$formula_path" \
  "$current_url" \
  "$current_sha256" \
  "$sdist_url" \
  "$sdist_sha256" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
current_url, current_sha256, next_url, next_sha256 = sys.argv[2:]
contents = path.read_text()
current_stanzas = f'  url "{current_url}"\n  sha256 "{current_sha256}"'
next_stanzas = f'  url "{next_url}"\n  sha256 "{next_sha256}"'

if contents.count(current_stanzas) != 1:
    raise SystemExit(
        f"expected exactly one matching URL/SHA stanza in {path}, refusing to edit"
    )

path.write_text(contents.replace(current_stanzas, next_stanzas, 1))
PY

update_resources() {
  brew update-python-resources \
    --ignore-main-package-cooldown \
    --version="$version" \
    --package-name="$package" \
    "$formula_ref"
}

if ! update_resources; then
  echo "Homebrew resource resolution failed; retrying the same command once." >&2
  update_resources
fi

resolved_version="$(brew info --json=v2 "$formula_ref" | python3 -c 'import json, sys; print(json.load(sys.stdin)["formulae"][0]["versions"]["stable"])')"
if [ "$resolved_version" != "$version" ]; then
  echo "formula resolved to $resolved_version after update, expected $version" >&2
  exit 1
fi
