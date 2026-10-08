# Reflection: iraf-community_iraf

Activity pattern: irregular. Longest gap: 2000-01 to 2002-06 (30 months). Gaps of 3+ months: 23. Current status: Active.

IRAF has the longest and most irregular history in the set, starting in 1989 with 294 of 442 months empty and 23 gaps of three or more months. Activity arrives in bursts: 368 commits in 2008, 475 in 2017 and 744 in 2023. The longest gap runs from 2000-01 to 2002-06 (30 months).

The gap looked alarming but turned out to be an artefact. The commits on both sides are release snapshots by a generic 'IRAF' author ('IRAF PCIX Version 2.11.3' in December 1999, 'IRAF DUNX Version 2.12.1' in July 2002), so the early git history is a reconstruction of NOAO release tarballs and the gap is just the interval between two official releases. The real story is the 2017 community takeover after NOAO ended support: new maintainers led by Ole Streicher have kept IRAF building on modern systems, and the most recent commits add OpenSSL and TLS support and merge v2.18.1 changes, with an original NOAO developer contributing. The project recovered through new people and remains active.
