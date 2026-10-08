# Reflection: flyaflya_causact

**Longest gap:** 2022-09 to 2023-06 (10 months) · **Gaps of 3+ months:** 6 · **Pattern:** irregular · **Status:** Active (README rule)

## Inactivity patterns
causact is a single-maintainer R package (Adam Fleischhacker, also committing as `flyaflya`). Its activity comes in bursts tied to milestones: development in 2019 (191 commits), the JOSS paper in 2022, the backend switch in 2023, and patch releases in 2024–2025. These bursts are separated by six gaps of 4–10 months.

## Was the longest gap easy to interpret?
Easy. The ten commits before the gap (July–August 2022) all finish the JOSS paper: fixing Figure 3, a citation fix, typo fixes in examples, and "Add JOSS badge to readme". v0.4.3 was tagged for the Zenodo/JOSS archive on 2022-08-01. The ten commits after the gap (from 2023-07-31) are a backend migration: "changes that will not screw up greta… next batch of commits that tries to bring in numpyro", "got numpyro and install issues working", "exchanging greta for numpyro in examples". The package NEWS for 0.5.2 (published on CRAN on 2023-08-19) confirms "Switched inference to Python's numpyro; dag_greta() is now deprecated."

## Likely reasons
- **Inactivity:** a natural stopping point. The paper was published and v0.4.2 was on CRAN, so the maintainer had nothing urgent left to do.
- **Recovery:** trouble with the greta/TensorFlow backend ("install issues") pushed a rewrite onto numpyro (JAX). It was the same person, with no new contributors.
- **Since then:** the recent commits are releases and fixes forced by dependencies (JAX 0.7.1 broke `dag_numpyro()`, ArviZ was removed as a dependency, ggplot2 changes). This kind of package mostly moves when its ecosystem breaks it. The last commit was 2025-09-12 (release 0.6.0), so it is Active by the 2025-09-30 rule but has had no commits for a year as of October 2026.
