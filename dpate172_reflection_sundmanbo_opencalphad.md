# sundmanbo_opencalphad

NetID: dpate172

Longest gap: **2024-01 through 2024-05 (5 months)**. Activity pattern: **declining**.

OpenCalphad has a five-month gap from January through May 2024 after model, XML-format, and bug-fix work. Its [historical change log](https://github.com/sundmanbo/opencalphad/blob/bef99c408b9a59e75a5f374a88c2fbecff0456b8/changes.txt) gives useful context: the maintainer described slow development and part-time work during retirement in 2023, then recorded renewed multicomponent MQMQA work in June 2024. Limited available time is therefore a reasonable hypothesis, but the log does not prove why each gap month was empty. Bo Sundman returns for two sampled commits; eight later commits come from the previously unseen raw identity zhongjingjogy and mostly address compilation, tests, and CI. This is intermittent recovery rather than an immediate steady stream. A [later comment about unsupported Python bindings](https://github.com/sundmanbo/opencalphad/issues/57#issuecomment-2395505367) also identifies competing tasks, but it was written in October and should not be treated as direct evidence of the earlier pause.

**Before / after themes:** Feature development:Bug fixes / Other:Feature development. The samples contain 10 commits before and 10 after the gap.

**Recovery:** Yes. Commit bef99c4 and the June 18, 2024 changes.txt entry restart work on multicomponent MQMQA and Kohler–Toop extrapolations. October commits then concentrate on compilation, tests, and CI; the first ten post-gap commits span June through October rather than continuous monthly activity. Bo Sundman <bo.sundman@gmail.com> returns for the first two post-gap commits. The remaining eight are by zhongjingjogy <zhongjingjogy@gmail.com>, a raw identity absent from all dated pre-gap history.

**Status as of September 30, 2025:** Active. The latest eligible [GitHub commit](https://github.com/sundmanbo/opencalphad/commit/e1f8cb75310b58e6fac152254cdcc5c8e6f15152) is dated 2025-05-13T09:11:01Z. The 10 most recent eligible commits give **Other:Bug fixes**. This uses the assignment's April 1, 2025 cutoff and GitHub committer dates; the Part 1 lastGHCommitDate field keeps its later collection snapshot.

The gap samples use UTC author dates from Part 1, which includes commits outside the GitHub default branch. Recent themes use the saved default-branch history through the historical cutoff. Returning/new comparisons use complete pre-gap author strings; different names or emails can belong to the same person.

Sources:

- [Supporting evidence](https://github.com/sundmanbo/opencalphad/blob/bef99c408b9a59e75a5f374a88c2fbecff0456b8/changes.txt): Entries describe slow/part-time development in 2023 and renewed MQMQA work on 2024-06-18; source of the limited-time hypothesis.
- [Supporting evidence](https://github.com/sundmanbo/opencalphad/issues/57): A May 29, 2024 question concerns the old Python interface; a same-day reply gives installation guidance, so issue discussion continued during the author-time gap.
- [Supporting evidence](https://github.com/sundmanbo/opencalphad/issues/57#issuecomment-2395505367): On October 6, Bo Sundman says Python support is unavailable because of other tasks; evidence of competing priorities after, not a direct explanation of, the gap.
- [Supporting evidence](https://github.com/sundmanbo/opencalphad/commit/efda8a80e136588d95748c37ba175092fa5a5939): Diff changes the GEIN argument convention and model handling, clarifying the vague pre-gap message.
- [Supporting evidence](https://github.com/sundmanbo/opencalphad/commit/7ad968aed26de7cd4bbd23cf5495686e97f84aa0): Diff separates XML routines into an included source file, supporting the XML development label.
- [Supporting evidence](https://github.com/sundmanbo/opencalphad/commit/fc124e71a793fb5419ea2849ec02ddd56576ebd5): Mixed routine reorganization, cleanup, and worked-example changes; supports a maintenance classification for this broad commit.
