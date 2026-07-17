#!/usr/bin/env python3
"""Keep the public release catalog aligned with verified Homebrew formulas."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PACKAGES = ("lightnow-cli", "lightnow-proxy")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def version_tuple(value: str) -> tuple[int, int, int]:
    if not VERSION_RE.fullmatch(value):
        raise ValueError(f"invalid release version: {value}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def formula_version(root: Path, package: str) -> str:
    formula = (root / "Formula" / f"{package}.rb").read_text()
    normalized = package.replace("-", "_")
    match = re.search(rf"/{normalized}-([0-9]+\.[0-9]+\.[0-9]+)\.tar\.gz\"", formula)
    if match is None:
        raise ValueError(f"could not determine {package} version from its formula")
    return match.group(1)


def load_catalog(root: Path) -> dict[str, object]:
    catalog = json.loads((root / "releases.json").read_text())
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported release catalog schema")
    packages = catalog.get("packages")
    if not isinstance(packages, dict) or set(packages) != set(PACKAGES):
        raise ValueError("release catalog must contain exactly the supported packages")
    for package in PACKAGES:
        entry = packages.get(package)
        if not isinstance(entry, dict) or not isinstance(entry.get("version"), str):
            raise ValueError(f"release catalog entry is invalid: {package}")
        version_tuple(entry["version"])
    return catalog


def check_catalog(root: Path) -> None:
    catalog = load_catalog(root)
    packages = catalog["packages"]
    assert isinstance(packages, dict)
    for package in PACKAGES:
        entry = packages[package]
        assert isinstance(entry, dict)
        catalog_version = entry["version"]
        expected = formula_version(root, package)
        if catalog_version != expected:
            raise ValueError(
                f"{package} catalog version {catalog_version} does not match formula {expected}"
            )


def update_catalog(root: Path, package: str, version: str) -> bool:
    if package not in PACKAGES:
        raise ValueError(f"unsupported formula: {package}")
    requested = version_tuple(version)
    verified = formula_version(root, package)
    if verified != version:
        raise ValueError(
            f"refusing to publish {package} {version}; verified formula is {verified}"
        )

    catalog = load_catalog(root)
    packages = catalog["packages"]
    assert isinstance(packages, dict)
    entry = packages[package]
    assert isinstance(entry, dict)
    current = str(entry["version"])
    if version_tuple(current) > requested:
        raise ValueError(
            f"refusing to downgrade {package} catalog from {current} to {version}"
        )
    if current == version:
        return False

    entry["version"] = version
    catalog["generated_at"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    target = root / "releases.json"
    target.write_text(json.dumps(catalog, indent=2) + "\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?", choices=PACKAGES)
    parser.add_argument("version", nargs="?")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.check:
            if args.package or args.version:
                parser.error("--check does not accept a package or version")
            check_catalog(root)
        else:
            if args.package is None or args.version is None:
                parser.error("package and version are required")
            update_catalog(root, args.package, args.version)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
