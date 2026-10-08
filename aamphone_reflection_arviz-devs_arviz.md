# Reflection: arviz-devs_arviz

**Longest gap:** 2017-04 to 2018-02 (11 months) · **Gaps of 3+ months:** 3 · **Pattern:** declining · **Status:** Active

## Inactivity patterns
All three gaps of 3+ months (2015-11 to 2016-04, 2016-06 to 2016-12, 2017-04 to 2018-02) fall before 2018. In that period the repository was not yet ArviZ: its README called it *mcmcplotlib*, "Python package to plot MCMC samples". It started in 2015 with Thomas Wiecki's "Move over current pymc3.plots submodule" and had only 36 commits in three years. After March 2018 the project never paused again. Activity rose to about 2,000–2,500 commits a year in 2019–2020, then declined to 236–395 a year in 2023–2025.

## Was the longest gap easy to interpret?
Fairly easy, once I looked at the README rather than just the commit messages. The commits before the gap (Ari Hartikainen's string-formatting and local-import fixes, and Osvaldo Martin's "update to pymc3's plots stats and diagnostics") show a small copy of PyMC3 code being kept in sync. The commits after the gap say exactly what changed: "begin pymc3-independence process" (2018-03-06), then tests and a traceplot. The README was renamed from mcmcplotlib to ArviZ on 2018-03-23 (PR #34).

## Likely reasons
- **Inactivity:** the standalone copy had no release and no users, and plotting development still happened inside PyMC3, so there was nothing pulling people to this repo.
- **Recovery:** a deliberate relaunch as a backend-independent library. The same author (Osvaldo Martin, `aloctavodia`) restarted it, but growth came from new people: Agustina Arroyuelo (from 2018-04), Colin Carroll (2018-05), Ravin Kumar (2018-08) and Oriol Abril (2018-11). There are 320 distinct authors after the gap versus 7 before.
- **Later decline:** this reads as maturity rather than abandonment. Recent commits are mostly documentation for the 1.0 migration guide plus Dependabot updates, and releases continue (v1.0.0 in 2026-03, v1.3.0 in 2026-08).

## Caveat
WoC reports 9,492 commits against 1,670 on GitHub's `main`, because WoC counts every branch and fork commit attributed to the project. The shape of the curve is still informative, but absolute numbers overstate work on the main line.
