# Reflection: genouest_biomaj-download

**Longest gap:** 2022-12 to 2024-03 (16 months) · **Gaps of 3+ months:** 5 · **Pattern:** declining · **Status:** Active (README rule)

## Inactivity patterns
The download micro-service for BioMAJ had busy periods in 2016 (97 commits) and 2019–2020 (about 150 a year). Activity then almost stopped: 6 commits in 2021, 8 in 2022, 0 in 2023. A small revival followed in 2024 (38) and very little after. The five gaps of 3+ months cluster in 2021–2025.

## Was the longest gap easy to interpret?
Yes, once I compared who committed before and after. Olivier Sallou wrote 186 of the 505 commits, 8 of the 10 commits just before the gap, and the last one ("fix direct handler for plugin usage", 2022-11-17, after release 3.2.9). After that, nobody committed for 16 months. Every author after the gap is new to the project except Brice Raffestin, who came back in 2025.

## Likely reasons
- **Inactivity:** the main developer stopped working on it, and the tool was mature enough that nobody else needed to touch it.
- **Recovery:** dependency breakage rather than new features. On 2024-04-19 Remy Siminel opened PR #43 "fix requirement" (setup.py and requirements.txt), merged the same day by Anthony Bretaudeau. Next came "pin protobuf dep" (#45) and "remove dependency on old Mock" (#44, Alexandre Detiste), and release 3.2.12 shipped on 2024-08-22. The PR has no description, so "keeping it installable" is my reading of the file changes.
- **Who:** new people (Remy Siminel, `mboudet`, Alexandre Detiste, Anthony Bretaudeau) kept it alive at maintenance level. Olivier Sallou did not return.
- **Now:** the latest commits are small download bug fixes merged in May 2025. That passes the 2025-09-30 Active rule, but it looks like a project on life support rather than one in development.
