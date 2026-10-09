# scifio_scifio-imageio

The supplied activity pattern is **irregular**, with 14 reported gaps. The longest observed internal gap runs from **2022-06 through 2024-05**, or 24 complete months without a commit. The last preceding commit is dated 2022-05-31; the first following commit is dated 2024-06-19.

## Interpretation

Low-frequency upkeep of an ITK-dependent module is a plausible explanation. The last pre-gap messages concern ITK upgrades; the data do not establish that a blocked migration caused the pause.

Matt McCormick restarted recorded work by upgrading CI to ITK 5.4.0 on 2024-06-19. Later commits update macros, formatting and CI compatibility, which supports an ecosystem-maintenance interpretation.

Matt McCormick and Hans Johnson are returning contributors already present before the gap. The first ten returning records show no newly observed contributor identities.

The 24 empty months are clear in the dataset, but commits provide no explicit abandonment notice. The restart is understandable as compatibility maintenance, and repeated equivalent messages under different hashes should not be mistaken for independent features.

## Status and recent work

As of **2026-09-30**, the project is **Active** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-04-22**, while the latest available commit message is dated **2025-06-27**. The status date used is **2026-04-22**. The supplied GitHub date was not independently reverified. Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.

Before-gap themes: Dependency updates:Other. After-gap themes: Dependency updates:Other. Themes in latest available sample: Other:Dependency updates.

## Evidence

### Before gap

Theme counts: Dependency updates (5), Other (4), Bug fixes (1).

- 2020-11-11 · `250dbde3d2aecfc5c8ca54428b759cf0af309aa7` · Mathew Seng · Other: ENH: Disable azure-pipelines.yml for new GitHub Actions
- 2020-11-11 · `b2194bf6d1ed3df9518b7af55d118279b18bdf83` · Mathew Seng · Bug fixes: BUG: ITK runtime directory in PATH for Windows not specified
- 2020-11-18 · `7f4355bc5301c9eeaef03fd07b0d1fab10fa9354` · Mark Hiner · Other: Merge pull request #69 from mseng10/update-github-actions
- 2021-01-11 · `549c7176c3faa65c6fd1bcd66cf7c6f9298a3208` · Mathew Seng · Other: COMP: Update GitHub Actions from ITKModuleTemplate
- 2021-01-15 · `fea74f7899d9c265c7b937292c984bb92df6c312` · Matt McCormick · Other: Merge pull request #70 from mseng10/update-ci
- 2021-12-18 · `ac0060f3d296beab6e1e82886bf0d1c61aaab65e` · Hans Johnson · Dependency updates: COMP: Modules need updated version of ITK
- 2021-12-18 · `42b30ee7d50ef6c91e0d3153f400b62bc114b2f7` · Hans Johnson · Dependency updates: COMP: Modules need updated version of ITK
- 2021-12-18 · `f6916932ec283a94782aef6ff5af5ed80d3c5833` · Hans Johnson · Dependency updates: COMP: Modules need updated version of ITK
- 2022-05-31 · `1054ece893ee072bdb8124c45ce207de00af280f` · Tom Birdsong · Dependency updates: ENH: Bump ITK and replace http with https using script
- 2022-05-31 · `76e1d922d3128e3ac351348f8af83a05b7e3db3e` · Tom Birdsong · Dependency updates: ENH: Bump ITK and replace http with https using script

### After gap

Theme counts: Dependency updates (4), Other (4), Documentation updates (2).

- 2024-06-19 · `850ef484464844c010e08fa822149439dc79687a` · Matt McCormick · Dependency updates: ENH: Upgrade CI for ITK 5.4.0
- 2024-06-19 · `6ce7630ea6bb4ef7588b12a3da4b9c53570f6c84` · Matt McCormick · Dependency updates: ENH: Upgrade CI for ITK 5.4.0
- 2025-01-26 · `52c4f224299d1fcffec69c9cac4003e81ab0158e` · Hans Johnson · Documentation updates: STYLE: Add itkVirtualGetNameOfClassMacro + itkOverrideGetNameOfClassMacro
- 2025-01-26 · `f361073559d74bdbece157acf62f6253af016e2d` · Hans Johnson · Documentation updates: STYLE: Add itkVirtualGetNameOfClassMacro + itkOverrideGetNameOfClassMacro
- 2025-01-27 · `0395fe3bd56cb8e67fec3a47f664c750bac234f1` · Hans Johnson · Other: STYLE: Update to match clang-format-19 from ITK
- 2025-01-27 · `8177fd4b8328b066e6654af2756863873c86123d` · Hans Johnson · Other: STYLE: Update to match clang-format-19 from ITK
- 2025-01-28 · `8533deebf417f1ef720f3b0e5d8e7c128b99889b` · Hans Johnson · Other: ENH: Update to support the clang-format-linter CI
- 2025-01-28 · `9750d13c1b62675f7f368d670f5076fdd5b29d24` · Hans Johnson · Other: ENH: Update to support the clang-format-linter CI
- 2025-03-09 · `299358464280d729052a33eccd887456335b44ab` · Hans Johnson · Dependency updates: ENH: Use latest actions, do not pin to latest version
- 2025-03-09 · `651d653b5252196f5ebd9e518d9e298736ac7860` · Hans Johnson · Dependency updates: ENH: Use latest actions, do not pin to latest version

### Latest available sample before cutoff

Theme counts: Other (8), Dependency updates (2).

- 2025-03-27 · `0c563353ea9c89f6024fe54ca7a3b8f254d36895` · Hans Johnson · Other: ENH: Use standard CI build mechanisms.
- 2025-03-27 · `f7ad3cc999994921b717a66553e281f20d028114` · Hans Johnson · Other: ENH: Use standard CI build mechanisms.
- 2025-05-27 · `79092d7930ad15e6b39a1a64ffcb8aef72ffac5e` · Hans Johnson · Dependency updates: ENH: Remove examples and update to v5.4.3 build
- 2025-05-27 · `ebd2fbb226dc8f5167f2d3a18df7d83914dfb5f4` · Hans Johnson · Dependency updates: ENH: Remove examples and update to v5.4.3 build
- 2025-05-27 · `069fe7a394ebd2aab429b1cb0b537fa162d22562` · Hans Johnson · Other: ENH: Update to remove python CI
- 2025-05-27 · `60444f02f228653209a470f686ead9f086fd2707` · Hans Johnson · Other: ENH: Update to remove python CI
- 2025-05-27 · `911983a668c0d56810275df8c05cf61a6314fbda` · Hans Johnson · Other: COMP: Add tracking of master branch.
- 2025-05-27 · `b95a988053b3b83e326ad87bd9f4942276d39c3b` · Hans Johnson · Other: COMP: Add tracking of master branch.
- 2025-06-27 · `20b6615ad165c36a5e7baace8214308929c52435` · Dženan Zukić · Other: COMP: Change the tracked ITK branch from master to main
- 2025-06-27 · `801cdfb29d9129767ad46150815f9b597b532294` · Dženan Zukić · Other: COMP: Change the tracked ITK branch from master to main

## External check

[https://github.com/scifio/scifio-imageio](https://github.com/scifio/scifio-imageio)

Repository and closed-PR retrieval were unavailable. Interpretation therefore relies on the supplied commit messages, with no claim that issue discussion established the cause.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.
- Original last commit date 2026-04-22 differs from summary maximum 2025-06-27; original value retained as a separate-source metric.
