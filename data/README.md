# Data provenance

`penguins.csv` is an unchanged copy of the Palmer penguins simplified dataset:

https://raw.githubusercontent.com/allisonhorst/palmerpenguins/8957207b78d6ccd1b4654a9dd9c9041b657478ab/inst/extdata/penguins.csv

Downloaded 2026-09-18. Upstream commit:
`8957207b78d6ccd1b4654a9dd9c9041b657478ab`.
The local file's SHA-256 is recorded in `SHA256SUMS` (paths relative to repository root).
The application reads this bundled snapshot and performs no network data access.

344 observations, 8 columns: species, island, bill_length_mm, bill_depth_mm,
flipper_length_mm, body_mass_g, sex, year. Collection years: 2007 to 2009.
Missing values are represented by `NA`; 2 rows have missing physical measurements
and 11 have missing sex. The application preserves these in exploration.

Data were collected by Dr. Kristen Gorman and the Palmer Station LTER program.
Data license: CC0, as stated by the original package:
https://allisonhorst.github.io/palmerpenguins/

Suggested citation: Horst AM, Hill AP, Gorman KB (2020). palmerpenguins:
Palmer Archipelago (Antarctica) penguin data. doi:10.5281/zenodo.3960218.

This is a small observational dataset, not a random sample of all penguins.
Rows have no individual identifier in this simplified table; duplicates are
rejected, but distinct rows cannot prove that individuals are independent.
