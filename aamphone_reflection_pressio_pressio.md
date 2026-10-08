# Reflection: pressio_pressio

**Longest gap:** 2021-05 (1 month) · **Gaps of 3+ months:** 0 · **Pattern:** declining · **Status:** Active

## Activity pattern
Pressio (C++ model-reduction library) was never really inactive: there are no gaps of three months or more, and the longest zero-commit stretch is a single month. Volume peaked at about 1,000 commits a year in 2019–2020, then declined to 457 (2021), 372 (2022), a spike to 615 (2023), and 171–222 (2024–2025). I classed it as declining because the long-run level dropped about fivefold even though work never stopped.

## Was the longest gap easy to interpret?
Easy. The commits before it (2021-04-28/29) are a release push by Francesco Rizzi: CI and test clean-up, website rebuilds, "rom: fix solve functions for pressio4py" and "cmake: update version". v0.10.0 was tagged on 2021-04-29. May 2021 then had no commits. Work resumed with a website update on 2021-06-22, API refactors ("extent is a free function #297", refactor for #298) and a code-wide clang-format pass (#116).

## Likely reasons
- **The one-month pause** is a normal break after a release, not a sign of trouble.
- **Who:** the same lead developer (Francesco Rizzi, 949 commits after the gap) plus new contributors such as Mikołaj Zuzek (345, starting with the formatting work), Cezary Skrzyński, Caleb Schilly and Marcin Wróbel.
- **Decline:** the drop after 2020 matches a library moving from heavy initial development to maintenance and periodic releases (0.15.0 in 2025-04, 0.17.0 in 2025-09). The recent commits are version bumps, license and header checks, CI against a new Trilinos release, and clang fixes.
