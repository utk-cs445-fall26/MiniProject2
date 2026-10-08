# Reflection: peal_vole

**Longest gap (as computed):** 2014-04 to 2019-10 (67 months) · **Gaps of 3+ months:** 6 · **Pattern:** irregular · **Status:** Active

## Inactivity patterns
Taken at face value, the timeline starts with one commit in March 2014, then nothing for five and a half years. After that come steady work from late 2019, a large burst in 2021 (424 commits, more than 100 in a single month), and a much quieter 2022–2025. There are five more gaps of 3–8 months: one in 2020 and four in 2023–2025.

## Was the longest gap easy to interpret?
It was hard at first, and the answer is that it is not a real gap. The only commit before it is "Squash of all gh-pages history up to 2021-07-30" by Max Horn. That commit lives on the `gh-pages` (website) branch, and its author date, 2014-03-21, is most likely inherited from the GAP package-website template that Max Horn maintains. A squash commit written in 2021 cannot really date from 2014. The project itself starts with Chris Jefferson's "Initial commit" on 2019-11-14, and its first ten commits are early development ("Updates", "Move code around"). So the 67 months measure how old a website template is, not how long the project was abandoned.

## Likely reasons for the real gaps
- The **longest real gap** is 8 months (2023-12 to 2024-07). Before it, Chris Jefferson was doing clean-up ("Fix clippy suggestions", "Remove unused package"). After it, on 2024-08-27, he bundled BacktrackKit and GraphBacktracking and updated dependencies, which led to release v0.6.0 in January 2025. This looks like a research-software rhythm: work happens in bursts when the main author has time or a paper or release to finish.
- **Who:** the project depends heavily on Chris Jefferson, with Wilf Wilson (278 commits) as the other major contributor; Max Horn only touches the website template. Recent commits (June–July 2026) are Chris adding refiners and a daemon mode, so the project is active again.

## Lesson
Commit timestamps can be inherited from templates or imported history. The first thing to check for a suspiciously early first commit is the branch it lives on and its message.
