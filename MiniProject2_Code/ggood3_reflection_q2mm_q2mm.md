# q2mm_q2mm

The supplied activity pattern is **U-shaped**, with 5 reported gaps. The longest observed internal gap runs from **2021-01 through 2022-10**, or 22 complete months without a commit. The last preceding commit is dated 2020-12-10; the first following commit is dated 2022-11-30.

## Interpretation

Development distributed across separate code versions is plausible. The first returning message explicitly describes unifying four code versions, so a quiet main history may conceal work elsewhere rather than complete inactivity.

A merge/rebase unifies four versions, followed by imported group code, Amber functionality and atom-order fixes. This is concrete evidence of code consolidation accompanying recovery.

Mikaela Farrugia/mmfarrugia is newly observed after the gap and supplies most of the sampled restart work. Eric Hansen is a returning contributor. Email matches connect the Farrugia aliases.

The 22 empty months are easy to measure but harder to interpret as abandonment. The recovery messages provide a stronger explanation than generic claims about a research hiatus because they explicitly describe consolidation of parallel code versions.

## Status and recent work

As of **2026-09-30**, the project is **Active** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-04-20**, while the latest available commit message is dated **2025-08-05**. The status date used is **2026-04-20**. The supplied GitHub date was not independently reverified. Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.

Before-gap themes: Feature development:Other. After-gap themes: Bug fixes:Other. Themes in latest available sample: Bug fixes:Feature development.

## Evidence

### Before gap

Theme counts: Feature development (4), Other (3), Bug fixes (2), Documentation updates (1).

- 2019-10-09 · `7cda5c376d6e76ebc2a7231e8b7fb11ada389062` · John E. Herr · Bug fixes: Merge pull request #66 from Q2MM/bug/issue-57
- 2019-10-09 · `5adc047fba4dac3768847cc13c15ba54d98e1df4` · Eric Hansen · Other: Merge branch 'q2mm/master' into eric/master
- 2019-10-24 · `f0380670b3003930f101258430506fe02051fa3a` · Kevin Koh · Feature development: Hessian weight assignment for Macromodel
- 2019-10-24 · `166dd73f48764faf1bc9696726b3f84255e1bda4` · Kevin Koh · Other: Merge branch 'master' of https://github.com/Q2MM/q2mm
- 2019-10-24 · `e0726de7258fdbec7a805b10320cb2d512c020a9` · Kevin Koh · Documentation updates: sch_util.py description
- 2019-10-24 · `b99fd6cde49c5be173698a99f04edcac3e417919` · Kevin Koh · Other: Merge e0726de7258fdbec7a805b10320cb2d512c020a9 into 7cda5c376d6e76ebc2a7231e8b7fb11ada389062
- 2020-03-13 · `b6e06c8500bdfd7822f339af4e7cec9dbf576955` · Kevin Koh · Bug fixes: fixed datalbl in calculate.py -> deleted lines in compare.py
- 2020-06-15 · `cc4b30ec4d8613ea91b2bfdb01147872abcca260` · Kevin Koh · Feature development: parameter.py for amber
- 2020-12-10 · `2907212266959d95deab5ce378f5e0391ba97ca3` · Kevin Koh · Feature development: HMGR parameters and Pymol uploaded
- 2020-12-10 · `8e0145516045ced43f1e3a863c32d1078be8b5d0` · Kevin Koh · Feature development: HMGR

### After gap

Theme counts: Other (4), Bug fixes (4), Feature development (2).

- 2022-11-30 · `4ab8440fe5645f15777b5e604015e7e86b1364ac` · Mikaela Farrugia · Other: Merge and rebase commit, rebased merge onto eric-master to maintain linear history after unifying 4 code versions
- 2022-12-06 · `59c99a1d4e3bc5e4ab9a3feeb22dd85e32cfb8ce` · mmfarrugia · Bug fixes: initial-from-group-afs + BUG: fixatomorder + amber fxnlty
- 2022-12-12 · `2672cf0d34e2e2af00bb4836e1220584b0eb1b5f` · mmfarrugia · Feature development: initial from afs group q2mm_jacobian
- 2022-12-12 · `217b33d99aabd123d4984c167d5b47c7df817b68` · mmfarrugia · Bug fixes: FIX:bug fixes and logger fix + initial from nsf-c-cas/q2mm-2
- 2023-03-12 · `a20159fa2f487250df15d40f8c8a5fd12adc1e51` · Eric Hansen · Other: Merge remote-tracking branch 'q2mm/master'
- 2023-05-30 · `fabe03c2910f4d6f0b19d5e80b88f70304f6e8f3` · Mikaela Farrugia · Other: Merge pull request #74 from ericchansen/master
- 2023-06-12 · `feaaadfc6dc30bd24eda903b4d69485444c5d8dc` · mmfarrugia · Other: update logger levels add note to gradient purposes
- 2023-06-27 · `b77dffb5dd6f2211c0c04e9f24b6632bea8b36d4` · mmfarrugia · Feature development: ADD: add back in screen directory - no changes
- 2023-06-27 · `d6cb5f711141f5ff2660d580837b3e99cbe9674c` · mmfarrugia · Bug fixes: FIX: fix screen directory
- 2023-06-30 · `461cbd8707ad01461b2fdb7553504890f0a9a4c0` · mmfarrugia · Bug fixes: FIX: remove buggy jacobian file write per Brock note

### Latest available sample before cutoff

Theme counts: Bug fixes (4), Feature development (3), Other (3).

- 2025-05-02 · `4d4cc251a82a29363bd24a4507754939fde7dfbd` · mmfarrugia · Feature development: ADD: Cisplatin FUERZA final SI files and analysis
- 2025-05-02 · `981d9652681ad97590b279c14f787af6aae1c4af` · mmfarrugia · Other: updated cisplatin gsff ipynb
- 2025-05-02 · `ab156bf30ab3cd9bca7fb82fbdebbdb0271b9224` · mmfarrugia · Feature development: ADD: rh hydrogn enamides fuerza SI
- 2025-05-11 · `78631bf87f5938fc4a27ca07af4be46df3c71372` · mmfarrugia · Other: updated cjskgauup
- 2025-05-12 · `023b7eb797273ca72737503f8c4d8aecdee82ba0` · mmfarrugia · Bug fixes: FIX: calculate import of sch_utils
- 2025-08-05 · `0bb114691c4a4ba99292b6543bb602a576b63fb2` · mmfarrugia · Other: updated ff plotting and fuerza figure notebooks
- 2025-08-05 · `ccac5efc1232d23e72088d217a0398d81f20bd86` · mmfarrugia · Bug fixes: FIX: swarm instantiation check and reset
- 2025-08-05 · `b121aa8e9c42778de0dbf3ba8ecd2ab0d5e9bac1` · mmfarrugia · Bug fixes: FIX: logging import
- 2025-08-05 · `4740d4d93588a6ff1c4cd19f4858ae26e8f872ba` · mmfarrugia · Bug fixes: FIX: actually checks if loose spread indicated in inputs
- 2025-08-05 · `f6f1538c82859998243e4d0e4491cdb720de42de` · mmfarrugia · Feature development: ADD: incomplete, under dev but a feature add, parameter dependency check

## External check

[https://github.com/Q2MM/q2mm/pull/74](https://github.com/Q2MM/q2mm/pull/74)

Repository and PR #74 retrieval were unavailable. Evidence of unification and imported code comes from the supplied messages.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.
- Original last commit date 2026-04-20 differs from summary maximum 2025-08-05; original value retained as a separate-source metric.
