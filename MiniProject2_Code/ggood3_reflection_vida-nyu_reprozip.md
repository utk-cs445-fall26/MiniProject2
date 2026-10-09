# vida-nyu_reprozip

The supplied activity pattern is **declining**, with 3 reported gaps. The longest observed internal gap runs from **2025-02 through 2025-11**, or 10 complete months without a commit. The last preceding commit is dated 2025-01-27; the first following commit is dated 2025-12-08.

## Interpretation

A pause in release and maintenance work is plausible, but the records do not state why work stopped. The final pre-gap records are merge commits on 2025-01-27, following test, buffer and documentation maintenance.

Work resumed with the 1.3.1 release on 2025-12-08, followed by 1.3.2 and compatibility changes. Release notes identify GCC 14 build and path-buffer fixes for 1.3.1, supporting maintenance-driven recovery rather than a demonstrated change in funding or staffing.

Remi Rampin led the resumption and Brian Hoffman also reappeared. Alexandre Detiste is newly observed in the supplied project history after the gap. Returning versus new identities were checked against all pre-gap records.

The gap is easy to locate but difficult to explain causally. Release activity resumed by January 2026, but the newest supplied activity is still before April 2026, so recovery from an earlier gap does not imply Active status at the September 2026 cutoff.

## Status and recent work

As of **2026-09-30**, the project is **Inactive** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-01-18**, while the latest available commit message is dated **2026-02-04**. The status date used is **2026-02-04**. The supplied GitHub date was not independently reverified. RecentThemes uses the latest ten available summary records.

Before-gap themes: Other:Bug fixes. After-gap themes: Other:Dependency updates. Themes in latest available sample: Other:Dependency updates.

## Evidence

### Before gap

Theme counts: Other (7), Bug fixes (2), Documentation updates (1).

- 2024-11-26 · `2ae8fd928242e890554e1a44c0e1de49caedeb1a` · Remi Rampin · Other: CI: Run Ubuntu 20.04 test in container
- 2024-11-26 · `0ddc884a32b6883d559241ddf6cb15fc924cfa83` · Remi Rampin · Other: tests: Use HEAD but ignore 501 from vagrantup.com
- 2024-11-26 · `e1ae2848f9296fa9f2c7548f5013be7030b458d6` · Remi Rampin · Other: tests: More logging during image checks
- 2024-11-26 · `64c743651d13e28006c3598e661adf7207eaa5d3` · Remi Rampin · Other: Merge branch 'test-vagrant-images' into '1.x'
- 2024-11-29 · `fa5e2507de596c544a3fafadce09c6ac0294d78c` · Remi Rampin · Bug fixes: Initialize buffer to empty
- 2024-12-02 · `686c235c303bbb0f47a59887790e68b82aaebe00` · Remi Rampin · Bug fixes: Merge pull request #396 from VIDA-NYU/proc-path-buffer
- 2024-12-02 · `bdd6546964f4bf1b56d59955c5cdaa78e84c1935` · Remi Rampin · Documentation updates: docs: Fix intersphinx conf
- 2025-01-27 · `49b1bb04463e952883ff3e57910847dc3ceed3c4` · Brian Hoffman · Other: Merge 991ffac69501dda00972e59ccd30d4afaa6a5dd2 into bdd6546964f4bf1b56d59955c5cdaa78e84c1935
- 2025-01-27 · `cf85c1ad523c78adb204ac918901e0a7eecdbe1e` · Remi Rampin · Other: Merge ad75c23d005bddf6a9672daff82e39a8b59ece30 into bdd6546964f4bf1b56d59955c5cdaa78e84c1935
- 2025-01-27 · `0d41913a61ecc9208f81fc0429cec646978b20fb` · Remi Rampin · Other: Merge 0edec88ab63cb1b724af291579a74a654d0bbe07 into bdd6546964f4bf1b56d59955c5cdaa78e84c1935

### After gap

Theme counts: Other (4), Release (2), Dependency updates (2), Documentation updates (1).

- 2025-12-08 · `4fa2646ce2c7279f6f174c5d20e543cccb71b0f3` · Remi Rampin · Release: Bump version to 1.3.1
- 2026-01-18 · `44687ce73efe7a889bf7a1ea982258e2d965c766` · Remi Rampin · Release: Bump version to 1.3.2
- 2026-01-21 · `13564f4ff92bc3e6437d75c3aaf6ba940ca31ceb` · Remi Rampin · Other: Merge 0edec88ab63cb1b724af291579a74a654d0bbe07 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-21 · `9c11a08e481565262516441e230e276496834ef1` · Remi Rampin · Other: Merge ad75c23d005bddf6a9672daff82e39a8b59ece30 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-21 · `749d90515d3b2ecbcaf962e4b728bfb4d7c0d585` · Brian Hoffman · Other: Merge 991ffac69501dda00972e59ccd30d4afaa6a5dd2 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-22 · `af0f16b6a25de360eb22d951e14b735c10f141a2` · Alexandre Detiste · Dependency updates: drop Python2 support which is effectively broken by recent usage of importlib_metadata
- 2026-01-22 · `21c7873d0b37935bd9915216930ccc8abbe18ec7` · Alexandre Detiste · Dependency updates: Merge af0f16b6a25de360eb22d951e14b735c10f141a2 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-02-04 · `1583fe7ff47dd3605a14c8f458ea7641ce92ce0c` · Remi Rampin · Documentation updates: Add .well-known/security.txt
- 2026-02-04 · `811f5c3f7a35c68bb1e0d1871ca6c578f9ad4ffb` · Remi Rampin · Other: Add .nojekyll

### Latest available sample before cutoff

Theme counts: Other (5), Release (2), Dependency updates (2), Documentation updates (1).

- 2025-01-27 · `0d41913a61ecc9208f81fc0429cec646978b20fb` · Remi Rampin · Other: Merge 0edec88ab63cb1b724af291579a74a654d0bbe07 into bdd6546964f4bf1b56d59955c5cdaa78e84c1935
- 2025-12-08 · `4fa2646ce2c7279f6f174c5d20e543cccb71b0f3` · Remi Rampin · Release: Bump version to 1.3.1
- 2026-01-18 · `44687ce73efe7a889bf7a1ea982258e2d965c766` · Remi Rampin · Release: Bump version to 1.3.2
- 2026-01-21 · `13564f4ff92bc3e6437d75c3aaf6ba940ca31ceb` · Remi Rampin · Other: Merge 0edec88ab63cb1b724af291579a74a654d0bbe07 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-21 · `9c11a08e481565262516441e230e276496834ef1` · Remi Rampin · Other: Merge ad75c23d005bddf6a9672daff82e39a8b59ece30 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-21 · `749d90515d3b2ecbcaf962e4b728bfb4d7c0d585` · Brian Hoffman · Other: Merge 991ffac69501dda00972e59ccd30d4afaa6a5dd2 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-01-22 · `af0f16b6a25de360eb22d951e14b735c10f141a2` · Alexandre Detiste · Dependency updates: drop Python2 support which is effectively broken by recent usage of importlib_metadata
- 2026-01-22 · `21c7873d0b37935bd9915216930ccc8abbe18ec7` · Alexandre Detiste · Dependency updates: Merge af0f16b6a25de360eb22d951e14b735c10f141a2 into 44687ce73efe7a889bf7a1ea982258e2d965c766
- 2026-02-04 · `1583fe7ff47dd3605a14c8f458ea7641ce92ce0c` · Remi Rampin · Documentation updates: Add .well-known/security.txt
- 2026-02-04 · `811f5c3f7a35c68bb1e0d1871ca6c578f9ad4ffb` · Remi Rampin · Other: Add .nojekyll

## External check

[https://github.com/VIDA-NYU/reprozip/releases](https://github.com/VIDA-NYU/reprozip/releases)

Release notes retrieved: 1.3.1 lists GCC 14 and path-buffer fixes; 1.3.2 lists replacement of deprecated pkg_resources. PR #396 could not be retrieved.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- RecentThemes uses the latest ten available summary records.
- Stats reports 3243 commits; summary has 3244 unique hashes; original metric retained.
- Original last commit date 2026-01-18 differs from summary maximum 2026-02-04; original value retained as a separate-source metric.
