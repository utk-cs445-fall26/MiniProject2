# Reflection: clindatsci_dicomweb-python-client

**Longest gap:** 2024-11 to 2025-03 (5 months) · **Gaps of 3+ months:** 3 · **Pattern:** U-shaped · **Status:** Active

## Inactivity patterns
The client was steadily active from 2018 to 2022, with 45–142 commits a year and frequent releases (v0.1 to v0.59). It then fell into a trough: 17 commits in 2023 and 24 in 2024. All three gaps of 3+ months sit in that trough (2023-10 to 2024-01, 2024-03 to 2024-05, 2024-11 to 2025-03), and activity picked up again in 2025 (48 commits), which gives the U shape. The repository has since moved from `clindatsci` to `ImagingDataCommons/dicomweb-client`.

## Was the longest gap easy to interpret?
The *before* side was easy. The ten commits before the gap are one release push by Chris Bridge in October 2024: a move to pyproject.toml, support for Python 3.11–3.13, a CLI-name revert, and "Version bump for release" (v0.59.2 and v0.59.3). The *after* side needed outside evidence. The first post-gap commits include merges of PRs #2 and #3 "from openradx/…", which turned out to be from a fork. The upstream pull request #108 ("Additional get params", linked to issue #105) explains who these contributors are: openradx developers who use the client in their ADIT project and needed extra query parameters.

## Likely reasons
- **Inactivity:** a feature-complete library maintained on demand. After the October 2024 release, nothing was asked of the maintainers for five months.
- **Recovery:** downstream users drove it. Sumantra Sharma (19 commits), Kai Schlamp (9), Jaya Krishnan S R (6) and Lachlan Newman (1) are all new. The returning maintainers Chris Bridge and Steve Pieper reviewed and merged PR #108 on 2025-05-13 and released v0.60.0 on 2025-05-24.
- **Now:** the 10 latest commits are almost all bug fixes from outside contributors (streaming multipart decoding, closing file pointers), merged through 2026-08. That fits a stable library that its users maintain.
