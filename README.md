# Homebrew Tap for LightNow

This repository publishes public Homebrew formulas:

- `lightnow-cli`

It also contains a release template for:

- `lightnow-proxy`

`Formula/lightnow-cli.rb` is based on the published PyPI `lightnow-cli` 1.0.3
source distribution.

`Formula/lightnow-proxy.rb.in` remains a template until the first
`lightnow-proxy` release exists, because Homebrew formulas must pin stable URLs
and SHA256 checksums.

## User Install Commands

Install the LightNow CLI:

```sh
brew tap lightnow-ai/tap
brew install lightnow-cli
```

`lightnow-proxy` will be available through Homebrew after the first
`lightnow-proxy` package release.

## Release Checklist

1. Publish the Python package release.
2. Verify the GitHub Release contains the distribution artifacts.
3. Generate or update the formula from the release artifact URL and SHA256.
4. Run:
   ```sh
   brew audit --strict --online Formula/lightnow-cli.rb
   brew audit --strict --online Formula/lightnow-proxy.rb
   brew install --build-from-source Formula/lightnow-cli.rb
   brew install --build-from-source Formula/lightnow-proxy.rb
   brew test Formula/lightnow-cli.rb
   brew test Formula/lightnow-proxy.rb
   ```
5. Commit and push the formula updates.

## Repository Setup

Create the GitHub repository as:

- Owner: `lightnow-ai`
- Name: `homebrew-tap`
- Default branch: `main`

Homebrew users will reference it as `lightnow-ai/tap`.
