"""Compute gap, activity, and theme evidence from a WoC project-summary CSV.

Used for MiniProject3 validation of kbissonn and reused for MiniProject2.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter

import pandas as pd

csv.field_size_limit(sys.maxsize)

THEME_RULES = [
    ("Automated bot contributions", r"dependabot|github-actions|\[bot\]|auto-?merge|pre-commit|semantic-release"),
    ("Security patches", r"\bcve\b|security|vulnerab"),
    ("Dependency updates", r"dependenc|bump |upgrade |compat:|compat\b|requirements|pyproject|cargo|composer"),
    ("Release", r"\brelease\b|changelog|version bump|prepare .*release|v\d+\.\d+"),
    ("Documentation updates", r"\bdoc(s|umentation)?\b|readme|typo|comment|tutorial|example"),
    ("Bug fixes", r"\bfix(e[sd])?\b|bug|hotfix|patch|regress|error|crash|issue #?\d+"),
    ("Feature development", r"\badd(ed|s|ing)?\b|\bfeat(ure)?\b|implement|support for|introduc|new "),
]


def load_summary(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", dtype=str, engine="python", on_bad_lines="warn")
    df.columns = [c.strip().strip("[]") for c in df.columns]
    msg_col = "commit message" if "commit message" in df.columns else "commit_message"
    df = df.rename(columns={msg_col: "message", "project_wocid": "project"})
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df = df.dropna(subset=["time", "project"]).copy()
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["month"] = df["dt"].dt.strftime("%Y-%m")
    df["message"] = df["message"].fillna("").str.replace("\n", " ", regex=False).str.strip()
    return df


def classify_message(message: str) -> str:
    text = message.lower()
    for theme, pattern in THEME_RULES:
        if re.search(pattern, text):
            return theme
    return "Other"


def top_themes(messages: list[str], k: int = 2) -> str:
    if not messages:
        return "Other:Other"
    counts = Counter(classify_message(m) for m in messages)
    ranked = [theme for theme, _ in counts.most_common()]
    while len(ranked) < k:
        ranked.append("Other")
    return ":".join(ranked[:k])


def monthly_series(group: pd.DataFrame) -> pd.Series:
    counts = group.groupby("month").size().sort_index()
    start = pd.Period(counts.index[0], freq="M")
    end = pd.Period(counts.index[-1], freq="M")
    idx = [str(p) for p in pd.period_range(start, end, freq="M")]
    return counts.reindex(idx, fill_value=0).astype(int)


def find_gaps(series: pd.Series) -> list[tuple[str, str, int]]:
    """Return (start, end, length) for every run of zero-commit months."""
    gaps = []
    start = None
    length = 0
    prev = None
    for month, n in series.items():
        if n == 0:
            if start is None:
                start = month
                length = 1
            else:
                length += 1
        else:
            if start is not None:
                gaps.append((start, prev, length))
            start = None
            length = 0
        prev = month
    if start is not None:
        gaps.append((start, prev, length))
    return gaps


def activity_pattern(series: pd.Series) -> str:
    y = series.to_numpy(dtype=float)
    n = len(y)
    if n < 6:
        return "irregular"
    third = max(n // 3, 1)
    first = y[:third].mean()
    mid = y[third : 2 * third].mean()
    last = y[2 * third :].mean()
    x = pd.Series(range(n), dtype=float)
    slope = float(pd.Series(y).corr(x))
    mean = y.mean() or 1.0
    cv = float(y.std() / mean)

    if mid < 0.45 * min(first, last) and min(first, last) > 0.5:
        return "U-shaped"
    if last < 0.55 * first and slope < -0.15:
        return "declining"
    if first < 0.55 * last and slope > 0.15:
        return "rising"
    # A repeated annual rise and fall shows up as a strong 12-month autocorrelation.
    if n >= 36:
        s = pd.Series(y)
        ac = s.autocorr(lag=12)
        if ac is not None and ac > 0.45 and cv > 0.6:
            return "cyclical"
    if cv > 1.15 or abs(slope) < 0.1 and cv > 0.8:
        return "irregular"
    return "steady"


def yearly_totals(series: pd.Series) -> str:
    tmp = series.copy()
    tmp.index = pd.PeriodIndex(tmp.index, freq="M")
    yearly = tmp.groupby(tmp.index.year).sum()
    return " ".join(f"{year}:{int(n)}" for year, n in yearly.items())


def snippet(messages: list[str], n: int = 8) -> str:
    lines = []
    for m in messages[:n]:
        text = re.sub(r"\s+", " ", m)[:110]
        lines.append(text)
    return " | ".join(lines)


def analyze_project(group: pd.DataFrame) -> dict:
    group = group.sort_values("time")
    series = monthly_series(group)
    gaps = find_gaps(series)
    long_gaps = [g for g in gaps if g[2] >= 3]
    if gaps:
        longest = max(gaps, key=lambda g: (g[2], g[0]))
    else:
        longest = None

    if longest:
        after = group[group["month"] > longest[1]]
        before = group[group["month"] < longest[0]]
    else:
        after = group.iloc[0:0]
        before = group

    before_msgs = before.tail(10)["message"].tolist()
    after_msgs = after.head(10)["message"].tolist()
    recent = group.tail(10)
    recent_msgs = recent["message"].tolist()[::-1]
    last_dt = group["dt"].max()
    active = "Active" if last_dt >= pd.Timestamp("2025-04-01", tz="UTC") else "Inactive"

    who = ""
    if len(after):
        who = after.iloc[0]["author"].split("<")[0].strip()

    return {
        "ncommits": int(len(group)),
        "nauthors": int(group["author"].nunique()),
        "from": group["dt"].min().strftime("%Y-%m-%d"),
        "to": last_dt.strftime("%Y-%m-%d"),
        "longest_start": longest[0] if longest else "",
        "longest_end": longest[1] if longest else "",
        "longest_len": longest[2] if longest else 0,
        "n_gaps_3": len(long_gaps),
        "commits_after": int(len(after)),
        "pattern": activity_pattern(series),
        "yearly": yearly_totals(series),
        "before_themes": top_themes(before_msgs),
        "after_themes": top_themes(after_msgs),
        "recent_themes": top_themes(recent_msgs),
        "who_after": who,
        "current": active,
        "has_recovered": "Yes" if longest and longest[2] >= 3 and len(after) > 0 else "No",
        "before_snip": snippet(list(reversed(before_msgs))),
        "after_snip": snippet(after_msgs),
        "recent_snip": snippet(recent_msgs),
        "series": series,
    }


def report(path: str) -> dict[str, dict]:
    df = load_summary(path)
    out = {}
    for project, group in df.groupby("project"):
        out[project] = analyze_project(group)
    return out


if __name__ == "__main__":
    results = report("partner_data/kbissonn_project_summary.csv")
    for project, r in results.items():
        print("=" * 88)
        print(project)
        for key in (
            "ncommits",
            "nauthors",
            "from",
            "to",
            "longest_start",
            "longest_end",
            "longest_len",
            "n_gaps_3",
            "commits_after",
            "pattern",
            "current",
            "has_recovered",
            "before_themes",
            "after_themes",
            "recent_themes",
            "who_after",
            "yearly",
        ):
            print(f"  {key}: {r[key]}")
        print("  BEFORE:", r["before_snip"])
        print("  AFTER:", r["after_snip"])
        print("  RECENT:", r["recent_snip"])
