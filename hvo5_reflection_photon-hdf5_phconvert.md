# photon-hdf5_phconvert

phconvert looks dead in the middle and is not. 2015 has 352 commits, the count slides to 2 in 2020 and 5 in 2021, 2022 and 2023 are empty, and 2024 has 101. That is U-shaped, and the right side of the U is lower than the left. Five gaps last three months or more. The longest is 35 months, June 2021 through April 2024.

The reason is not written down. The last commits before the hole make sure an HDF5 file gets closed, avoid copying an array, and add a contributor name. The first commits after it, from Paul Harris, who does not appear before the gap, add PTU file types, switch the build to setuptools_scm, and add GitHub Actions. A new person and a build-system move are what the return actually is. It is not a return to the 2015 volume.

The latest commits update the README for a release, move the docs to the pydata theme, and extend QC-card support. GitHub's last commit is 2026-09-08, so the project is Active. An empty year here was a pause, and the commit that ended it was ordinary maintenance plus one new file type.
