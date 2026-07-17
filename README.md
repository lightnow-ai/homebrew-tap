# Homebrew Tap for LightNow

This repository publishes public Homebrew formulas:

- `lightnow-cli`
- `lightnow-proxy`

Both formulas are generated from the corresponding published PyPI source
distribution. A successful package release dispatches a formula update to this
repository; the update is committed only after Homebrew audit, source install,
and formula tests pass.

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
4. The workflow commits the generated formula update directly to `main`.

For recovery or an initial backfill, run the `Update formula` workflow manually
with one of the two allowlisted formula names and an already published version.
The manual path performs exactly the same validation and update steps as a
release dispatch.

## Repository Setup

Create the GitHub repository as:

- Owner: `lightnow-ai`
- Name: `homebrew-tap`
- Default branch: `main`

Homebrew users will reference it as `lightnow-ai/tap`.
