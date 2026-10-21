"""Write MiniProject2 Part 2 and Part 3 files for hvo5.

Monthly counts, gaps, and first-pass themes come from analyze_evidence.py.
The activity labels, themes, and gap reasons below are the reviewed readings
of those series and of the commits on either side of the longest zero run.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import analyze_evidence as ae

ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / "hvo5_project_summary.csv"

# Stars, forks, and the default-branch commit date recorded in hvo5.ipynb on 2026-09-28.
GITHUB = {
    "juliaastro_astrolib.jl": (91, 25, "2026-07-08"),
    "cra-ros-pkg_robot_localization": (1962, 1039, "2026-07-16"),
    "hmri-group_hmri-toolbox": (86, 46, "2026-09-16"),
    "tdda_tdda": (311, 29, "2026-07-13"),
    "openspace_openspace": (1259, 210, "2026-09-26"),
    "photon-hdf5_phconvert": (17, 14, "2026-09-08"),
    "nocions_letswave6": (50, 32, "2026-09-20"),
    "flatsurf_flatsurf": (10, 4, "2025-12-17"),
    "mano-b_microsec": (6, 2, "2025-10-16"),
    "ablab_spades": (961, 165, "2026-09-28"),
}

ORDER = list(GITHUB)

# Qualitative fields, in ORDER. Computed fields (counts, dates, gap bounds) are not stored here.
QUAL = {
    "juliaastro_astrolib.jl": dict(
        pattern="declining",
        before="Bug fixes:Documentation updates",
        after="Bug fixes:Documentation updates",
        reason="Maintenance had already fallen from 298 commits in 2017 to about 20 a year, mostly generated doc builds. The last commits before the 9-month hole are a Mars-constants fix and a version bump, and none of them says why work paused. The likely cause is a thin maintainer base with nothing urgent to fix.",
        recovered="Yes",
        why="Henrik Wolf, who has no commits before the gap, fixes the sunpos docstring and an lsf_rotate inference regression. The pace then rises to 53 commits in 2024 and 71 in 2025, still far under the 2017 peak.",
        who="Henrik Wolf (no commits before the gap)",
        status="Active",
        recent="Automated bot contributions:Documentation updates",
        notes="Yearly commits peak at 298 in 2017 and then stay under 30 until a 9-month hole from 2022-11 to 2023-07. Henrik Wolf, a new name in the log, ends that hole with docstring and inference fixes, and 2024-2025 are busier without getting close to 2017. The latest commits are Dependabot bumps of GitHub Actions plus a README edit. GitHub's last commit is 2026-07-08, so the project is Active.",
    ),
    "cra-ros-pkg_robot_localization": dict(
        pattern="declining",
        before="Bug fixes:Feature development",
        after="Bug fixes:Feature development",
        reason="N/A active Project. The longest zero-commit run is two months (2025-06 to 2025-07), and the history has no gap of three months or more.",
        recovered="No",
        why="N/A",
        who="N/A",
        recent="Feature development:Documentation updates",
        status="Active",
        notes="Commits drift down from about 300-380 a year in 2014-2016 to about 70-100 in 2023-2025, so the long pattern is declining. The longest empty stretch in eleven years is still only two months, in mid-2025, with race-condition fixes on one side and a namespaced service plus a covariance fix on the other. There is no inactivity gap to explain. GitHub's last commit is 2026-07-16, so the project is Active.",
    ),
    "hmri-group_hmri-toolbox": dict(
        pattern="irregular",
        before="Bug fixes:Feature development",
        after="Release:Feature development",
        reason="The first 16 commits are small VBQ MATLAB-batch bug fixes on the old SVN branch. They stop in 2015-04, and the messages do not say why. The next commit is ten months later.",
        recovered="Yes",
        why="Martina Callaghan, already committing before the gap, tags a release that fixes output-folder sharing, and the FIL branch plus DICOM import then land in the shared repository. The author count goes from 2 before the gap to 42 after it.",
        who="Martina Callaghan (already committing before the gap), then the FIL branch",
        status="Active",
        recent="Bug fixes:Documentation updates",
        notes="Yearly commits swing from 354 in 2017 to 30 in 2019 and back to 271 in 2024, so the pattern is irregular. The longest hole, 2015-05 through 2016-02, is the move from the VBQ SVN branch into the shared hMRI repository, not the project dying. Martina Callaghan ends it with a release, and the author count grows from 2 to 42. GitHub's last commit is 2026-09-16, so it is Active.",
    ),
    "tdda_tdda": dict(
        pattern="U-shaped",
        before="Documentation updates:Feature development",
        after="Release:Dependency updates",
        reason="After 222 commits in 2018, 2020 has 4 and 2021 has 10. The commits just before the longest hole are gentest wizard work, a README tweak, and a doc-image update. None of them says why development stopped.",
        recovered="Yes",
        why="Nick Radcliffe, an author from before the gap, resumes on the 2.0 line: pyproject.toml, newer numpy and pandas pins, and gentest packaging. 2025 then has 331 commits, the busiest year in the history.",
        who="Nick Radcliffe (already committing before the gap)",
        status="Active",
        recent="Bug fixes:Feature development",
        notes="Commits rise to 222 in 2018, collapse in 2020-2021, and reach 331 in 2025, so this is U-shaped. The longest hole is 11 months, 2022-03 through 2023-01, and the commits on either side do not explain it. Nick Radcliffe, an existing contributor, ends it with the 2.0 release and packaging work. GitHub's last commit is 2026-07-13, so it is Active.",
    ),
    "openspace_openspace": dict(
        pattern="steady",
        before="Bug fixes:Other",
        after="Feature development:Dependency updates",
        reason="N/A active Project. Across 25,493 commits the longest zero-commit run is two months, 2015-08 to 2015-09, and there is no gap of three months or more.",
        recovered="No",
        why="N/A",
        who="N/A",
        status="Active",
        recent="Feature development:Other",
        notes="After a 2014-2015 ramp, yearly commits stay between about 1,800 and 3,400, so the pattern is steady. The longest empty stretch is two months in 2015, during the move to a new SGCT, and no gap reaches three months. There is no inactivity to recover from. GitHub's last commit is 2026-09-26, so it is Active.",
    ),
    "photon-hdf5_phconvert": dict(
        pattern="U-shaped",
        before="Other:Feature development",
        after="Dependency updates:Feature development",
        reason="The 2015 burst of 352 commits fades to 2 in 2020 and 5 in 2021, then 2022 and 2023 are empty. The last commits before the hole close an HDF5 file correctly, avoid a data copy, and add a name to the contributor list. They do not say the project was archived.",
        recovered="Yes",
        why="Paul Harris, who has no commits before the gap, adds PTU file types and moves the package onto setuptools_scm and GitHub Actions. 2024 has 101 commits. That does not reach the 2015 volume, but it is a real return.",
        who="Paul Harris (no commits before the gap)",
        status="Active",
        recent="Documentation updates:Feature development",
        notes="A busy 2015, two empty years, and 101 commits in 2024 make this U-shaped with a partial recovery. The longest hole is 35 months, 2021-06 through 2024-04, and the commit text does not say why it opened. Paul Harris, new to the project, ends it with new PTU file types and a build-system move. GitHub's last commit is 2026-09-08, so it is Active.",
    ),
    "nocions_letswave6": dict(
        pattern="declining",
        before="Bug fixes:Feature development",
        after="Feature development:Other",
        reason="Commits fall from 169 in 2015 to a handful a year. The messages just before the hole are an STFT update, an SSEP explore fix, and a Neurone bugfix. They do not say why work stopped.",
        recovered="Yes",
        why="André Mouraux, an author from before the gap and the only author after it, adds center-of-gravity amplitude to the ROI explorer. It is one commit. The project resumed, and it did not return to its old rate.",
        who="André Mouraux (already committing before the gap)",
        status="Active",
        recent="Feature development:Bug fixes",
        notes="Commits decline from 169 in 2015 to one in 2023 and none in 2024. The longest hole is 29 months, 2023-02 through 2025-06, and only one commit follows it, a small ROI feature by André Mouraux. That counts as a recovery, but not a return to the old pace. WoC's last commit (2025-07-10) and GitHub's (2026-09-20) are both after the cutoff, so it is Active.",
    ),
    "flatsurf_flatsurf": dict(
        pattern="declining",
        before="Release:Bug fixes",
        after="Dependency updates:Other",
        reason="The only gap of three months or more sits directly after the 3.13.3 version bump, its changelog, and a doctest fix. It reads as a pause after a release. No message says the library was abandoned.",
        recovered="Yes",
        why="Julian Rüth, already a maintainer before the gap, comes back to build maintenance: conda-forge pins, dropping Python 3.7, and building with fmt 10. 266 commits follow the hole.",
        who="Julian Rüth (already committing before the gap)",
        status="Active",
        recent="Automated bot contributions:Dependency updates",
        notes="Yearly commits fall from 692 in 2020 to about 110 in 2024-2025, so the pattern is declining. The only gap of three months or more is a 5-month pause right after the 3.13.3 release in 2023. Julian Rüth, an existing maintainer, ends it with dependency and toolchain updates, and the latest commits are Dependabot bumps. GitHub's last commit is 2025-12-17, so it is Active.",
    ),
    "mano-b_microsec": dict(
        pattern="U-shaped",
        before="Other:Other",
        after="Bug fixes:Documentation updates",
        reason="2020 has 324 commits and 2022 is down to 13. The ten commits before the hole are all bare 'Update <file>.R' lines, so they do not say what stopped and they do not name a theme.",
        recovered="Yes",
        why="shibatay2301, who has no commits before the gap, fixes stringr handling of DNAStrings and then updates the BAM loader, the homology code, and the README. 2024 has 192 commits, close to the early pace.",
        who="shibatay2301 (no commits before the gap)",
        status="Active",
        recent="Documentation updates:Other",
        notes="Yearly counts of 324, 123, 13, 1, 192, and 1 make this U-shaped. The 14-month hole from 2022-03 through 2023-04 is preceded only by bare 'Update file.R' commits, so the reason is not in the text. shibatay2301, new to the project, ends it with bug fixes and README updates. GitHub's last commit is 2025-10-16, after the cutoff, so it is Active.",
    ),
    "ablab_spades": dict(
        pattern="declining",
        before="Documentation updates:Other",
        after="Bug fixes:Other",
        reason="N/A active Project. The longest zero-commit run in 15 years and 18,459 commits is the single month 2025-06. There is no gap of three months or more.",
        recovered="No",
        why="N/A",
        who="N/A",
        status="Active",
        recent="Bug fixes:Other",
        notes="Commits fall from 4,442 in 2011 to 128 in 2025, so the pattern is declining, but the project never stops. The longest empty run is the single month 2025-06, so there is no inactivity gap. The latest commits fix the barcode encoder and a graph iterator and add tests. GitHub's last commit is 2026-09-28, so it is Active.",
    ),
}


def write_timeseries(results: dict) -> None:
    for project in ORDER:
        series = results[project]["series"]
        frame = pd.DataFrame({"Month": series.index, "#Commits": series.to_numpy()})
        frame.to_csv(ROOT / f"hvo5_commits_timeseries_{project}.csv", sep=";", index=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        x = range(len(series))
        ax.plot(list(x), series.to_numpy(), color="#1f4e79", lw=1.2)
        labels = list(series.index)
        step = max(len(labels) // 8, 1)
        ticks = list(range(0, len(labels), step))
        ax.set_xticks(ticks)
        ax.set_xticklabels([labels[i] for i in ticks], rotation=45, ha="right")
        ax.set_title(project)
        ax.set_xlabel("Time (YYYY-MM)")
        ax.set_ylabel("Number of Commits")
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(ROOT / f"hvo5_timeseries_{project}.png", dpi=300)
        plt.close(fig)


def write_gap_commits(summary: pd.DataFrame, results: dict) -> None:
    path = ROOT / "hvo5_project_gap_commits.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\n")
        writer.writerow(["pre_post", "project_wocid", "commit_sha1", "author", "time", "commit message"])
        for project in ORDER:
            group = summary[summary["project"] == project].sort_values("time")
            start, end = results[project]["longest_start"], results[project]["longest_end"]
            before = group[group["month"] < start].tail(10)
            after = group[group["month"] > end].head(10)
            for _, row in before.iterrows():
                message = " ".join(str(row["message"]).split())
                writer.writerow(["pre", project, row["commit_sha1"], row["author"], int(row["time"]), message])
            for _, row in after.iterrows():
                message = " ".join(str(row["message"]).split())
                writer.writerow(["post", project, row["commit_sha1"], row["author"], int(row["time"]), message])


def write_stats(results: dict) -> None:
    header = [
        "Project", "ncommits", "nauthors", "from", "to", "nstars", "nforks", "lastGHCommitDate",
        "LongestGapStart (YYYY-MM)", "LongestGapEnd (YYYY-MM)", "LongestGapLength (months)",
        "NumCommitsAfterLastGap", "ActivityPattern", "NumberOfGapsInTimeline",
        "BeforeThemes", "AfterThemes",
        "HypothesizedGapReason", "HasRecovered", "WhyRecovered", "WhoRecovered",
        "Currentstatus", "RecentThemes", "Notes",
    ]
    rows = []
    for project in ORDER:
        r = results[project]
        q = QUAL[project]
        stars, forks, last_gh = GITHUB[project]
        rows.append({
            "Project": project,
            "ncommits": r["ncommits"],
            "nauthors": r["nauthors"],
            "from": r["from"],
            "to": r["to"],
            "nstars": stars,
            "nforks": forks,
            "lastGHCommitDate": last_gh,
            "LongestGapStart (YYYY-MM)": r["longest_start"],
            "LongestGapEnd (YYYY-MM)": r["longest_end"],
            "LongestGapLength (months)": r["longest_len"],
            "NumCommitsAfterLastGap": r["commits_after"],
            "ActivityPattern": q["pattern"],
            "NumberOfGapsInTimeline": r["n_gaps_3"],
            "BeforeThemes": q["before"],
            "AfterThemes": q["after"],
            "HypothesizedGapReason": q["reason"],
            "HasRecovered": q["recovered"],
            "WhyRecovered": q["why"],
            "WhoRecovered": q["who"],
            "Currentstatus": q["status"],
            "RecentThemes": q["recent"],
            "Notes": q["notes"],
        })
    with (ROOT / "hvo5_project_stats.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REFLECTIONS = {
    "juliaastro_astrolib.jl": """# juliaastro_astrolib.jl

AstroLib.jl is a long decline with one real hole in it, not a project that ran out. Commits peak at 298 in 2017, then sit between 3 and 29 a year. Eight separate stretches last three months or more. The longest is nine months, November 2022 through July 2023.

The hole was not hard to bound and was hard to explain. The commits before it are a Mars-constants fix, a version bump, and generated documentation builds. Nothing says the library was being shut down. Henrik Wolf, who does not appear in the log before the gap, ends it by fixing the `sunpos` docstring and an `lsf_rotate` inference problem. 2024 and 2025 are busier (53 and 71 commits) and still nowhere near 2017, so the recovery is real and partial.

The latest commits are Dependabot bumps of GitHub Actions and a README edit. GitHub's last commit is 2026-07-08, after the 2025-04-01 cutoff, so the project is Active. A declining project can keep recovering from individual holes without ever getting its old pace back.
""",
    "cra-ros-pkg_robot_localization": """# cra-ros-pkg_robot_localization

robot_localization declines and does not stop. Yearly commits go from about 300 to 380 in 2014-2016 down to 69 in 2023 and about 100 in 2024-2025. Across the whole series there is no stretch of three empty months. The longest run of zero-commit months is June and July 2025.

That two-month run is easy to interpret because there is nothing to interpret. On one side are a race-condition fix, a 3.9.3 version, and a parameters callback. On the other are namespaced `enable` and `toggle` services and a covariance fix. The same kind of work is happening on both sides. The assignment's rule for a project with no inactivity gap applies: the reason for a gap is N/A, and HasRecovered is No.

Recent commits add an ECEF transform and update the IMU docs, alongside style fixes. GitHub's last commit is 2026-07-16, so the project is Active. The chart is a decline in volume, not a death.
""",
    "hmri-group_hmri-toolbox": """# hmri-group_hmri-toolbox

The hMRI toolbox does not have one direction. 2017 has 354 commits, 2019 has 30, and 2024 has 271. That is irregular. The longest hole is early and easy to see: May 2015 through February 2016, ten months, with only 16 commits before it.

Those early commits are VBQ MATLAB-batch bug fixes and a B1-mapping change on the old SVN branch, and they do not say why the work paused. The return is the move into the shared repository. Martina Callaghan, who was already committing, tags a release with an output-folder bug fix, and the FIL branch and the DICOM import follow. Two authors become 42. The gap is a reorganization, not abandonment.

Three gaps reach three months, and this is the longest. The latest commits fix the imperfect-spoiling correction and update the changelog. GitHub's last commit is 2026-09-16, so the project is Active.
""",
    "tdda_tdda": """# tdda_tdda

TDDA is the clearest U-shape in this set. Commits rise from 66 in 2016 to 222 in 2018, collapse to 4 and 10 in 2020 and 2021, and then 2025 has 331, more than the old peak. Six gaps last three months or more. The longest is 11 months, March 2022 through January 2023.

The hole is easy to measure and the reason is not in the text. Just before it, the commits are gentest wizard work, a README tweak, and a documentation image. Just after it, Nick Radcliffe, who was already an author, ships 2.0.03 through 2.0.05, adds `pyproject.toml`, and bumps numpy and pandas. The recovery is a release and a packaging cleanup by someone who had been there before, followed by the busiest year the project has had.

The latest commits repair `setup.py` and add discover flags. WoC's last commit is 2025-09-05 and GitHub's is 2026-07-13. Either date is after the cutoff, so the project is Active.
""",
    "openspace_openspace": """# openspace_openspace

OpenSpace is the project that never goes quiet. From 2016 through 2025 the yearly count stays between about 1,800 and 3,400 commits, after a smaller 2014-2015 ramp. That is steady. There is no gap of three months or more in 25,493 commits. The longest empty stretch is August and September 2015.

That stretch is a tooling change, not an inactivity gap. The commits before it fix the C++ standard flag and a Linux build. The commits after it move OpenSpace onto a new SGCT, update the fisheye config, and make a new GLM version compile. 23,988 commits follow. HasRecovered is No because nothing had stopped.

Recent work separates asset files and changes the minor-moons addon so trails are the default. GitHub's last commit is 2026-09-26, so the project is Active. A two-month hole inside a decade of continuous work should not be read as a recovery story.
""",
    "photon-hdf5_phconvert": """# photon-hdf5_phconvert

phconvert looks dead in the middle and is not. 2015 has 352 commits, the count slides to 2 in 2020 and 5 in 2021, 2022 and 2023 are empty, and 2024 has 101. That is U-shaped, and the right side of the U is lower than the left. Five gaps last three months or more. The longest is 35 months, June 2021 through April 2024.

The reason is not written down. The last commits before the hole make sure an HDF5 file gets closed, avoid copying an array, and add a contributor name. The first commits after it, from Paul Harris, who does not appear before the gap, add PTU file types, switch the build to setuptools_scm, and add GitHub Actions. A new person and a build-system move are what the return actually is. It is not a return to the 2015 volume.

The latest commits update the README for a release, move the docs to the pydata theme, and extend QC-card support. GitHub's last commit is 2026-09-08, so the project is Active. An empty year here was a pause, and the commit that ended it was ordinary maintenance plus one new file type.
""",
    "nocions_letswave6": """# nocions_letswave6

Letswave6 is a decline that nearly finishes. 2015 has 169 commits, 2016 has 84, and from 2019 on the count is in the single digits, with 2024 empty. Nine gaps last three months or more. The longest is 29 months, February 2023 through June 2025, and exactly one commit follows it.

That commit is the whole recovery. André Mouraux, who was already committing and is the only author after the gap, adds center-of-gravity amplitude to the ROI explorer. The messages before the hole are an STFT update, an SSEP fix, and a Neurone bugfix, and they do not say why the work stopped. HasRecovered is Yes because there is a new feature commit, and the note on it has to say that one commit is not the old project coming back.

WoC stops at 2025-07-10. GitHub's last commit is 2026-09-20. Both are after 2025-04-01, so the project is Active. The latest ten commits in the WoC file mix that one new feature with older bug fixes, because there are not ten commits after the gap.
""",
    "flatsurf_flatsurf": """# flatsurf_flatsurf

flatsurf declines smoothly and has almost no gaps. Commits go from 692 in 2020 to 329, 281, 138, 113, and 110. In the whole history only one stretch reaches three empty months: May 2023 through September 2023, five months, with 266 commits after it.

The hole was easy to interpret. It starts immediately after the 3.13.3 version bump, the changelog, and a doctest fix. That is a pause after a release. Julian Rüth, already a maintainer, comes back and does toolchain work: conda-forge pins, dropping Python 3.7, and fmt 10. No new person arrives, and the work that returns is maintenance rather than a new research direction.

The latest commits are Dependabot bumps of GitHub Actions. GitHub's default branch was last committed on 2025-12-17, which is after the cutoff, so the project is Active. WoC's newest commit is 2026-03-23 and comes from another branch. The decline in volume and the one post-release pause are separate facts, and only the second is a gap.
""",
    "mano-b_microsec": """# mano-b_microsec

MicroSEC is U-shaped. 2020 has 324 commits, 2021 has 123, 2022 has 13, 2023 has 1, and 2024 has 192. The longest hole is 14 months, March 2022 through April 2023. Three gaps reach three months. 194 commits follow the longest one.

The reason is not recoverable from the text. Every one of the ten commits before the hole says only "Update" and a filename, so there is no theme and no stated cause. The name that ends the hole, shibatay2301, does not appear before it. The first commits back fix `stringr` on DNAStrings and then update the BAM loader, the homology code, and the README. The 2024 count shows the return was sustained, not a single touch.

2025 has one WoC commit, and GitHub's last commit is the same day, 2025-10-16, which is still after the cutoff, so the project is Active. The latest messages are README edits and a file uploaded through the GitHub web UI. The right side of the U is real, and it is already thinning out again.
""",
    "ablab_spades": """# ablab_spades

SPAdes declines for fifteen years and never stops. 2011 has 4,442 commits, and the count steps down to 128 in 2025. There is no gap of three months or more. The longest run of empty months is June 2025, a single month, and 69 commits follow it.

There is no inactivity story to tell. Around that month the commits are a MkDocs deploy, a formatting fix in the docs, an Ubuntu runner bump, and then a dev-mode fix and an import cleanup. HasRecovered is No, and the gap reason is N/A, because the project was active the whole time. A long decline in volume is not a gap.

The latest commits fix the barcode encoder and a contracted-graph iterator and add tests for the barcode index. GitHub's last commit is 2026-09-28, the day the Part 1 snapshot was taken, so the project is Active. This is the case the coding guide is warning about: less work is not the same thing as stopped work.
""",
}


def write_reflections() -> None:
    for project, text in REFLECTIONS.items():
        (ROOT / f"hvo5_reflection_{project}.md").write_text(text.strip() + "\n")


def load() -> tuple[pd.DataFrame, dict]:
    summary = ae.load_summary(SUMMARY)
    results = {project: ae.analyze_project(summary[summary["project"] == project]) for project in ORDER}
    return summary, results


def main() -> None:
    summary, results = load()
    write_timeseries(results)
    write_gap_commits(summary, results)
    write_stats(results)
    write_reflections()
    for project in ORDER:
        r = results[project]
        print(
            f"{project}: gap {r['longest_start']}..{r['longest_end']} "
            f"({r['longest_len']} mo), after {r['commits_after']}, "
            f"gaps>=3 {r['n_gaps_3']}, pattern {QUAL[project]['pattern']}"
        )


if __name__ == "__main__":
    main()
