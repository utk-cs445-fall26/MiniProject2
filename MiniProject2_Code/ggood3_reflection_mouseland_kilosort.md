# mouseland_kilosort

The supplied activity pattern is **rising**, with 2 reported gaps. The longest observed internal gap runs from **2022-04 through 2022-10**, or 7 complete months without a commit. The last preceding commit is dated 2022-03-09; the first following commit is dated 2022-11-15.

## Interpretation

A development transition is plausible because recorded activity restarts with initial commits and new binary-processing work. This does not prove that the entire pause was spent on an architectural rewrite.

Returning commits introduce binary reading, filtering, simulation, template extraction and GUI work. The current README documents a newer Kilosort algorithm, which is context rather than direct proof of the 2022 inactivity cause.

Marius Pachitariu returned, including an email-only author alias. Carsen Stringer also returned: the pre-gap alias carsen-stringer has the same email. Shashwat Sridhar is newly observed in the supplied pre/post history and contributes initial GUI work.

The switch from README/merge activity to substantial development makes the restart interpretable. Author aliases and Former-commit-id records make raw author counts and commit counts imperfect measures of new people or independent work.

## Status and recent work

As of **2026-09-30**, the project is **Active** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-09-25**, while the latest available commit message is dated **2025-11-04**. The status date used is **2026-09-25**. The supplied GitHub date was not independently reverified. Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.

Before-gap themes: Documentation updates:Feature development. After-gap themes: Feature development:Bug fixes. Themes in latest available sample: Other:Bug fixes.

## Evidence

### Before gap

Theme counts: Documentation updates (6), Feature development (4).

- 2022-03-09 · `82d13887ea25c4568f6b35884aa71eb26ccaa163` · Marius Pachitariu · Feature development: Merge pull request #457 from mwawra/main
- 2022-03-09 · `fb822e79cb5dd4f55465ca951414dc8d25ee1643` · Marius Pachitariu · Feature development: Merge pull request #457 from mwawra/main
- 2022-03-09 · `d7f9fe341ae8f79ed8fe00a1b5af4120ada02d19` · Marius Pachitariu · Feature development: Merge pull request #386 from czuba/addGitTracking
- 2022-03-09 · `f74fbf8da802746e077e57299bf180379c787c0c` · Marius Pachitariu · Feature development: Merge pull request #386 from czuba/addGitTracking
- 2022-03-09 · `59399603045e52e28cce969d7cfa418b4b4a52af` · Marius Pachitariu · Documentation updates: Update README.md
- 2022-03-09 · `cb003a51c68880e8c3a9d26aa5c602c78e47d1ef` · Marius Pachitariu · Documentation updates: Update README.md
- 2022-03-09 · `9dc1ecdbf2d925e19a68a5661c1113a6eae3dcdf` · Marius Pachitariu · Documentation updates: Update README.md
- 2022-03-09 · `b898b2042d5c35755e92b64682e87e45646aed1a` · Marius Pachitariu · Documentation updates: Update README.md
- 2022-03-09 · `1a1fd3ae07a49c042b4128d6c2e79d6ab55872e5` · Marius Pachitariu · Documentation updates: Update README.md
- 2022-03-09 · `ebea0156c22dce8363040e78e56535709b130c2a` · Marius Pachitariu · Documentation updates: Update README.md

### After gap

Theme counts: Feature development (6), Other (2), Bug fixes (2).

- 2022-11-15 · `927562fe182f5ced3079aca23e6719c0f26129c0` · Marius Pachitariu · Other: Initial commit
- 2022-11-15 · `360f8d4fc544c70b820460ec4bbf7ecc13cafd9d` · marius10p@gmail.com · Other: initial commit
- 2022-11-16 · `afe135b2b3c48ac627fb98c14ad982ad5a0c2ac3` · Carsen Stringer · Feature development: binary reading and filtering for arbitrary time periods
- 2022-11-16 · `7c7432244ccf7835eb9f9a22e83ebdd805c7f96f` · Carsen Stringer · Feature development: finishing binary wrapper
- 2022-12-07 · `7c3d2045e51ede32ce5b018989066edc60dfb425` · Carsen Stringer · Feature development: adding simulation code
- 2022-12-07 · `20d97f21393e972b0f8f3921c50749388e313c8b` · marius10p@gmail.com · Feature development: changes to template extraction
- 2022-12-07 · `fd0a69fc34c3cc5f75cb3ada76c15b01b0e6830e` · marius10p@gmail.com · Bug fixes: fix error
- 2022-12-07 · `09c0244fafcb4eb33be5916d6ea3b2465b66932b` · marius10p@gmail.com · Bug fixes: needed swapped indices
- 2022-12-07 · `73b626c527a9e1f3b76fa6a43011653412684fbd` · Carsen Stringer · Feature development: updating kilosort to work with device input again
- 2022-12-08 · `ee2084a1a6da963a65faeed53d232d9583e1910b` · Shashwat Sridhar · Feature development: [gui] initial gui commit

### Latest available sample before cutoff

Theme counts: Other (5), Documentation updates (2), Bug fixes (2), Feature development (1).

- 2025-09-17 · `42fd52c962cc1ee2f6f6e2f04044c9f1bc4c8966` · Jacob Pennington · Feature development: Added option to downsample data batches when sorting
- 2025-09-19 · `cfb474f2ca1945fe3bf72f783909649677a0946d` · Alessio Buccino · Other: Merge 1f025171af4a2d63dd28c0617a3f6e1eb16cf8d5 into 42fd52c962cc1ee2f6f6e2f04044c9f1bc4c8966
- 2025-10-22 · `a96a45afdfa1eb21366a731b3b142c52f4fba994` · Jake Pennington · Other: Host logo in repo
- 2025-10-22 · `08febd76889acbceb1c0bf6e4d44c9aa1ac4eb3a` · Jake Pennington · Other: change logo host to repo instead of osf
- 2025-10-22 · `9d45e7f12eb9498539847eb0d68039210bcec738` · Jake Pennington · Documentation updates: Add logo to readme
- 2025-10-22 · `d5799b6c006e358e4cbf5ddfb618df6fb8be576b` · Jake Pennington · Documentation updates: reduce logo size in readme
- 2025-10-29 · `0a9860925ec09c99966cd994b7e077d9e9654e13` · Jacob Pennington · Bug fixes: Fix tmin indices for benchmark comparison
- 2025-10-29 · `63cb1a7869c7aaa73c6df0d35f7b3d32ff6fc90c` · Jacob Pennington · Other: Merge branch 'main' of github.com:MouseLand/Kilosort
- 2025-11-04 · `fdcc57a4cd87fc831729cf325603fff7d857b242` · Jacob Pennington · Bug fixes: Fixed path conversion to strings for filename saved in ops
- 2025-11-04 · `058244ebfc58b1beb61461dc75409dea652ea58d` · Jake Pennington · Other: Revert logo url to osf host

## External check

[https://github.com/MouseLand/Kilosort](https://github.com/MouseLand/Kilosort)

README retrieved and describes Kilosort4 as a new algorithm. PR #457 was unavailable. The README alone does not date or explain the earlier gap.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.
- Original last commit date 2026-09-25 differs from summary maximum 2025-11-04; original value retained as a separate-source metric.
