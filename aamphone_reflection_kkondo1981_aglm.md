# Reflection: kkondo1981_aglm

**Longest gap:** 2022-09 to 2025-04 (32 months) · **Gaps of 3+ months:** 6 · **Pattern:** declining · **Status:** Active (README rule)

## Inactivity patterns
aglm (an R package for accurate GLMs) was developed in bursts by essentially one person, Kenji Kondo (also committing as `kkondo1981`). There were bursts in 2019 (204 commits) and 2021 (111), with gaps of 3–6 months in between. After January 2022 there is almost nothing. A 32-month silence ends with a two-day burst in May 2025, and there have been no commits since.

## Was the longest gap easy to interpret?
Easy. The ten commits before it finish multinomial support in July 2021 (legend, margins and colour options for plots, forbidding residuals in multinomial cases). They are followed by "Small fixes and reran all demos on the new environment" (2022-01) and an automated PR merge reference in 2022-08. The ten commits after it are entirely about passing CRAN checks: "ignore missing package anchors NOTEs in CRAN build", "Added an import directive to avoid NOTEs in check()", "Added new cran-comments.md", PRs #67–#69 "Fix cran 202505", and "Submitted to CRAN". CRAN's records show version 0.4.0 published 2021-06-09 and 0.4.1 on 2025-05-12, with nothing in between.

## Likely reasons
- **Inactivity:** the package was feature-complete and stable on CRAN, and its single maintainer had no reason to change it.
- **Recovery:** an external obligation. R's CRAN checks began flagging issues (for example, missing package anchors in documentation links), and packages that keep failing checks risk being archived. The maintainer fixed just enough to publish 0.4.1. The same person did all of it.
- **Assessment:** this is a maintenance blip, not a real revival. It counts as Active only because the burst happened after 2025-04-01. Judged today it is dormant.
