# smistad_fast

The supplied activity pattern is **declining**, with 1 reported gaps. The longest observed internal gap runs from **2024-05 through 2024-07**, or 3 complete months without a commit. The last preceding commit is dated 2024-04-30; the first following commit is dated 2024-08-21.

## Interpretation

A short maintenance lull after the 4.9.2 release and tutorial updates is plausible. No supplied message says documentation stabilization caused the pause.

The first returning commit explicitly fixes issue #210, involving incorrect iteration over bytes and channels. Subsequent updates address the Clarius Cast dependency and build environments.

Erik Smistad authored all ten sampled post-gap commits and was already an established pre-gap contributor. Lisa Bonheme contributed the tutorial changes immediately before the gap.

This is a three-empty-month interruption, so it is weaker evidence of abandonment than the multi-year pauses elsewhere. Recovery is easy to identify from the explicit bug fix, while the inactivity cause remains uncertain.

## Status and recent work

As of **2026-09-30**, the project is **Needs verification** using the April 1, 2026 threshold. The uploaded stats file reports a GitHub last-commit date of **2026-10-07**, while the latest available commit message is dated **2025-11-06**. The status date used is **Unresolved: reported date is after cutoff**. The supplied GitHub date was not independently reverified. Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.

Before-gap themes: Other:Documentation updates. After-gap themes: Bug fixes:Dependency updates. Themes in latest available sample: Other:Feature development.

## Evidence

### Before gap

Theme counts: Other (5), Documentation updates (3), Feature development (1), Release (1).

- 2024-03-25 · `5332d05f3842227f2d9638dbb72c7a3a9b463c23` · Erik Smistad · Feature development: Implemented support for OME-TIFF whole slide image format
- 2024-03-25 · `cd4a3bbd6834895a735bef0164c955e377ca4a0d` · Erik Smistad · Other: Merge remote-tracking branch 'origin/master'
- 2024-03-25 · `7b186f9b7178e68d326044e8f46012b2acc5807a` · Erik Smistad · Other: Update CI-ubuntu.yml [no ci]
- 2024-03-25 · `4417e680042c62002b00cc1c981896ebf8ba8044` · Erik Smistad · Other: Update CI-windows.yml [no ci]
- 2024-03-25 · `d14eb6a6022409201641270ad4db26092e8ed868` · Erik Smistad · Other: Update CI-mac-x86_64.yml [no ci]
- 2024-03-25 · `43e794d46d02c6aeee2a1d092ebdc329fcb406ac` · Erik Smistad · Other: Update CI-mac-arm64.yml [no ci]
- 2024-03-25 · `bf5924572286bd13ada198ff495c843e967adb37` · Erik Smistad · Release: Bump to version 4.9.2 [no ci]
- 2024-04-29 · `1d298650e3dbd2cf6b2e0f4018cb3e3025d33b43` · Lisa Bonheme · Documentation updates: Show how to save files from PatchGenerator with the same file name format as ImagePyramidPatchExporter
- 2024-04-29 · `4e4782e741618172f3b2cbb53c6ceab8915ce69c` · Lisa Bonheme · Documentation updates: tiny typo fix
- 2024-04-30 · `019a556a2763f9c18264cb63f359f47fe5b78207` · Lisa Bonheme · Documentation updates: Update Python WSI tutorial documentation (#206)

### After gap

Theme counts: Bug fixes (3), Other (3), Dependency updates (3), Release (1).

- 2024-08-21 · `b8b4550a2870c2f4ca08a2c4bb301d163e48b25b` · Erik Smistad · Bug fixes: Fixed bug #210
- 2024-08-21 · `a3b631488488121fc0bb5539e35ac7db6352e8be` · Erik Smistad · Other: Merge remote-tracking branch 'origin/master'
- 2024-08-21 · `95067d75bab88130807bb3c461693da36cec8180` · Erik Smistad · Other: Update CI-ubuntu.yml [no ci]
- 2024-08-27 · `097b979dcf2d010f3c31bf4473002a0d020bd197` · Erik Smistad · Release: Bumped version number
- 2024-08-27 · `cb5ef54ccbc978f9c3dad6b8222e0d8f37275b0c` · Erik Smistad · Dependency updates: Upgraded Clarius Cast to version 11.2.0
- 2024-08-27 · `9ebed7dec7d6f0bae018ea1529ec146c6a55a776` · Erik Smistad · Other: Merge remote-tracking branch 'origin/master'
- 2024-08-27 · `d9d609cb9685cb2e13a15d8bd638f2aa03d62b73` · Erik Smistad · Bug fixes: Fixed missing license file after previous commit
- 2024-08-27 · `815a2794c971c37bef04ad6536ef5822e5ff5c87` · Erik Smistad · Dependency updates: Updated x86 mac github workflows to use macos-12 runner instead of macos-11 which has been removed from github [no ci]
- 2024-08-27 · `ff8b287f0aa7846edf114ca52b34ef2ecf01dc0f` · Erik Smistad · Dependency updates: Bump python version for Mac in pyenv to 3.7 as 3.6 doesn't compile on MacOS 12 [no ci]
- 2024-08-27 · `09e8d6c05dcc5747bd33b4b6014541a5ec5862c5` · Erik Smistad · Bug fixes: Pyenv python version Mac fix [no ci]

### Latest available sample before cutoff

Theme counts: Other (5), Feature development (2), Dependency updates (1), Release (1), Documentation updates (1).

- 2025-10-20 · `c13daaba2f71fc6fe4c1c261391bbc61fbc9359e` · Erik Smistad · Other: Missing package in CI-ubuntu [no ci]
- 2025-10-22 · `004bcb71dcbee028b438756249e1d2e5b5ae1205` · Erik Smistad · Dependency updates: Removed deb package dependency
- 2025-10-23 · `4254620a7458011d7669dcd573b79f8e70212d36` · Erik Smistad · Other: Update CI-ubuntu.yml [no ci]
- 2025-10-29 · `34f48b7d6ced9d6e6ae8a2be2adba63ac77b9fdf` · Erik Smistad · Release: Added sanity check when importing wsi with openslide and made estimation of magnification from spacing optional in ImagePyramid::getMagnification. Bumped version up to 4.14.1
- 2025-10-29 · `7d2868493ac903cab724666e1fe69ed34272db13` · Erik Smistad · Other: Merge remote-tracking branch 'origin/master'
- 2025-10-30 · `85cc02bb9865e50d7c4d7a1d31682b0dc965f49d` · Erik Smistad · Feature development: Added --no-gui option to systemCheck
- 2025-11-03 · `1706675a1b2bf0b2fb6cb258e948742fd4f84cf9` · Erik Smistad · Other: Update CI-ubuntu.yml [no ci]
- 2025-11-04 · `00f398b069a821b1a1a4410ad2a1cf85c9812c00` · Erik Smistad · Documentation updates: Added documentation on docker containers
- 2025-11-04 · `84576f5ba5104e53e23d327ea23bd8683b284d15` · Erik Smistad · Other: Merge remote-tracking branch 'origin/master'
- 2025-11-06 · `e87a1455731113f013167f1542658252bb1e8a3e` · Erik Smistad · Feature development: Added support for PyTorch tensors in Image and Tensor in pyFAST + tests

## External check

[https://github.com/FAST-Imaging/FAST/issues/210](https://github.com/FAST-Imaging/FAST/issues/210)

Issue #210 could not be retrieved at the old or current repository address. Its technical description is present in the supplied returning commit.

Commit hashes and quoted titles above come from the supplied CSV. Generated commit URLs in the evidence CSV are lookup aids; they were not all independently fetched. Current README text provides context only, not historical proof of why a gap occurred.

## Data notes

- Latest supplied messages predate the reported GitHub date; RecentThemes is provisional and requires the missing newer commits.
- The reported GitHub date is 2026-10-07, after the cutoff. No verified April-September 2026 commit was available, so historical status is unresolved rather than inferred from October activity.
- Original last commit date 2026-10-07 differs from summary maximum 2025-11-06; original value retained as a separate-source metric.
