# Homebrew Tap for LightNow

This repository publishes public Homebrew formulas:

- `lightnow-cli`
- `lightnow-proxy`

Both formulas are generated from the corresponding published PyPI source
distribution. A successful package release dispatches a formula update to this
repository; the update is committed only after Homebrew audit, source install,
and formula tests pass.

`releases.json` is the machine-readable catalog used by LightNow clients. It is
advanced only after the matching Homebrew formula has passed those checks, so a
listed version is ready for every supported installation channel.

## User Install Commands

Install the LightNow CLI:

```sh
brew tap lightnow-ai/tap
brew install lightnow-cli
```

Install the LightNow Local Proxy:

```sh
brew tap lightnow-ai/tap
brew install lightnow-proxy
```

## Automated Release Flow

1. `lightnow-cli` or `lightnow-proxy` publishes its package to PyPI.
2. The release workflow sends a `python-release-published` repository dispatch
   containing the formula and exact version.
3. `.github/workflows/update-formula.yml` verifies that the PyPI source
   distribution exists, regenerates the formula URL, checksum, and Python
   resources, then runs:
   ```sh
   brew style <formula>
   brew audit --strict --online <formula>
   brew install --build-from-source <formula>
   brew test <formula>
   ```
4. The workflow updates `releases.json` and commits the formula and catalog
   together directly to `main`.

For recovery or an initial backfill, run the `Update formula` workflow manually
with one of the two allowlisted formula names and an already published version.
The manual path performs exactly the same validation and update steps as a
release dispatch.

Validate catalog/formula consistency locally with:

```sh
python3 scripts/update-release-catalog.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
```

If a release was published but the catalog did not advance, re-run `Update
formula` for the exact package and version. The workflow is idempotent and
rejects catalog downgrades or a version that does not match the verified
formula.

## Repository Setup

Create the GitHub repository as:

- Owner: `lightnow-ai`
- Name: `homebrew-tap`
- Default branch: `main`

Homebrew users will reference it as `lightnow-ai/tap`.
