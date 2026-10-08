# Reflection: nbara_python-meegkit

**Longest gap (as computed):** 2009-01 to 2016-11 (95 months) · **Gaps of 3+ months:** 9 · **Pattern:** irregular · **Status:** Active

## Inactivity patterns
The WoC timeline begins with 39 commits in November–December 2008 by Pedro Alcocer, then nothing for almost eight years. From December 2016 the project is alive, with activity in short bursts (often around releases) separated by 3–8 month quiet periods. Yearly totals since 2018 range from 28 to 122 with no clear trend.

## Was the longest gap easy to interpret?
Moderately easy, once I checked the README. The pre-gap commits ("TSPCA and SNS both work with shifts again", "DSS works!") implement the same denoising methods meegkit provides today. The README says meegkit "is mostly a translation of Matlab code from the NoiseTools toolbox by Alain de Cheveigné. It builds on an initial python implementation by Pedro Alcocer." Nicolas Barascud (`nbara`) imported Pedro Alcocer's 2008 history when he created meegkit in December 2016; the first post-gap commits are "Create README.md" and "cleanup + gitignore". So the 95-month gap is pre-history from a different author, not a project that died and came back.

## Likely reasons
- **The "gap":** an imported repository history. The project as such starts in 2016-12. The longest *real* gap is 8 months (2017-01 to 2017-08), which ended with "Refactor code" (python 2→3, Travis, setup.py) in September 2017, when nbara turned the code into a proper package.
- **Who:** a different person (nbara, about 290 commits under two identities) revived the code, and over 30 contributors joined later. Pedro Alcocer never committed again.
- **Recent pattern:** releases come in bursts. In July 2026 there were several ASR bug fixes by Stefan Appelhoff and the 0.2.0 release, with Dependabot keeping CI actions current in between. The project remains active.
