# llnl_mgmol

The supplied activity pattern is **U-shaped**, with 2 reported gaps. The longest observed internal gap runs from **2022-03 through 2023-01**, or 11 complete months without a commit. The last preceding commit is dated 2022-02-04; the first following commit is dated 2023-02-03.

## Interpretation

An interruption between numerical-method development and later maintenance is plausible. FIRE work ends in February 2022, but completion of that work is not proof of the reason for inactivity.

The first returning commits repair mixed-precision builds and runs, followed by timing-script, finite-difference and LBFGS fixes. These identify the technical work that accompanied recovery, not the maintainer's private motivation.

Jean-Luc Fattebert authored all ten sampled post-gap commits and all ten sampled pre-gap commits. This is continuation by an established contributor.

The long pause and concentrated restart fit the supplied U-shaped activity label. The technical direction of recovery is clear, while the reason for the year-long interruption is not.

## Status and recent work

As of **2026-09-30**, the project is **Active** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-09-11**, while the latest available commit message is dated **2025-11-04**. The status date used is **2026-09-11**. The supplied GitHub date was not independently reverified. Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.

Before-gap themes: Bug fixes:Feature development. After-gap themes: Bug fixes:Other. Themes in latest available sample: Bug fixes:Other.

## Evidence

### Before gap

Theme counts: Bug fixes (6), Feature development (4).

- 2021-12-20 · `2f4edbead75452da14191f9a90097d637fc570a8` · Jean-Luc Fattebert · Bug fixes: Bug fix in LBFGS restart (#195)
- 2021-12-22 · `efd3dfbaf4a719e0e00893471789e93e18b5bbdf` · Jean-Luc Fattebert · Bug fixes: Add test for FIRE algorithm
- 2021-12-24 · `0cf475d3c59ee215c04dd06d5aa97730ce7000cd` · Jean-Luc Fattebert · Bug fixes: Add test for FIRE algorithm (#197)
- 2021-12-27 · `ffa39009c63ab21f3230569cc9337392b9922bcd` · Jean-Luc Fattebert · Bug fixes: Change mass used in FIRE algorithm
- 2021-12-28 · `5d82d12ab4cadaad90e3259da1d85fee02d9fa28` · Jean-Luc Fattebert · Bug fixes: Fix taum in FIRE algorithm
- 2021-12-29 · `1d376998d44f041e72717cd517448e048b4ec966` · Jean-Luc Fattebert · Bug fixes: Fix FIRE algorithm (#198)
- 2022-01-02 · `931856cafafb1e67f7702a7b69094a8e92240dac` · Jean-Luc Fattebert · Feature development: Add orthonormalization in Davidson
- 2022-01-03 · `d791c1ea32093556f1f4323fb3125513e7b9ec8a` · Jean-Luc Fattebert · Feature development: Add orthonormalization in Davidson (#199)
- 2022-02-03 · `c120dda7a677d43f18da93ae45832effc6731efa` · Jean-Luc Fattebert · Feature development: New FIRE implementation
- 2022-02-04 · `f04a0ee3c19b46d91e4868faff298a066eaa6cf6` · Jean-Luc Fattebert · Feature development: New FIRE implementation (#200)

### After gap

Theme counts: Bug fixes (8), Other (2).

- 2023-02-03 · `098e14200913a9b19dce08682da8e403f2cabd6a` · Jean-Luc Fattebert · Bug fixes: Fix a few lines to enable mixed-precision build
- 2023-02-04 · `63d5aa59580dd5a33316db9f0fe31ac7cd810626` · Jean-Luc Fattebert · Bug fixes: Fix a few lines to enable mixed-precision build (#201)
- 2023-02-08 · `7be3a05a35cdd2ced11478b583a44f80e8e780bb` · Jean-Luc Fattebert · Bug fixes: Fix mixed-precision run
- 2023-02-09 · `8231cdbfe65714816619843de491719193438d57` · Jean-Luc Fattebert · Bug fixes: Fix mixed-precision run (#202)
- 2023-02-23 · `8e10f13ab455aea8b7667ee69d88c74c9eea7116` · Jean-Luc Fattebert · Bug fixes: Fix script to compare timings between two runs
- 2023-02-23 · `dbe231d7177cc7f309a263f42bacb7a12c17291d` · Jean-Luc Fattebert · Other: Clean up use of 2nd order FD on coarse level
- 2023-02-24 · `8ca59d6adb580fa0fa9e23d160759a5daacaadf1` · Jean-Luc Fattebert · Other: Clean up use of 2nd order FD on coarse level (#203)
- 2023-02-24 · `0cdb289a7fe8e0a9c752de294b7ab863607287c4` · Jean-Luc Fattebert · Bug fixes: Fix script getTriatomicAngle for python3
- 2023-03-03 · `82dc1944553cbaad4a2ec9175d4f0234bde6ceb1` · Jean-Luc Fattebert · Bug fixes: Fix LBFGS solver
- 2023-03-04 · `84ed87c7cfcbf61f32c9d41eb80a11015a9813ea` · Jean-Luc Fattebert · Bug fixes: Fix LBFGS solver (#204)

### Latest available sample before cutoff

Theme counts: Bug fixes (7), Other (3).

- 2025-10-29 · `40ccaea2dfb378a1f4e0301c6f5c4ab998980ced` · Fattebert J.-L. · Other: Assume subdivx=1 in ExtendedGridOrbitals
- 2025-10-29 · `e1f3d0ccecadb7ad910a714d1d88a1f2a3de0a89` · Jean-Luc Fattebert · Other: Merge branch 'release' into nosubdivx_extended
- 2025-10-29 · `8e9902496efee68dee56cb98da4598147ac67f47` · Jean-Luc Fattebert · Other: Nosubdivx extended (#376)
- 2025-10-30 · `5ab62fd6653c876e720aee7e275938f4d4ecb4e1` · Jean-Luc Fattebert · Bug fixes: Fix compiler warnings
- 2025-10-30 · `535ff0a200e09ffbf974353ddee77865714fc185` · Jean-Luc Fattebert · Bug fixes: Fix several compiler warnings
- 2025-10-31 · `fc91b00392fbaca44004f7eb520e2e7ac4deb08e` · Jean-Luc Fattebert · Bug fixes: Fix several compiler warnings (#377)
- 2025-11-03 · `4526455a417e39aaf067a663f25a937b54f7bf65` · Jean-Luc Fattebert · Bug fixes: Fix some stdout content
- 2025-11-03 · `bc43b775e7265f1946130a8260542b4fc11ed57f` · Jean-Luc Fattebert · Bug fixes: Fix some stdout content (#378)
- 2025-11-03 · `e0a7e22a74521d20708ce7491db9e7b584f1088f` · Jean-Luc Fattebert · Bug fixes: Fix header of asci files generated by read_hdf5
- 2025-11-04 · `741af36c4a3f662d9aa95c8bf195dda0d80196b6` · Jean-Luc Fattebert · Bug fixes: Fix header of asci files generated by read_hdf5 (#379)

## External check

[https://github.com/llnl/mgmol](https://github.com/llnl/mgmol)

Repository overview retrieved; it describes the molecular-dynamics code. PR #201 could not be retrieved, so its description is supported only by the supplied merge/commit messages.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.
- Original last commit date 2026-09-11 differs from summary maximum 2025-11-04; original value retained as a separate-source metric.
