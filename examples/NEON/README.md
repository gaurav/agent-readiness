# Worked example: NEON's macroinvertebrate collection, DP1.20120.001

One dataset, taken through the whole method: what the dataset is, what its stewards wrote down
about it, where a coding agent handed it goes silently wrong, what the model-free index saw and
missed, what the LLM probes would find and what that finding would mean, and what a steward or a
reviewer of the idea should take from it. Every fact below was read on 2026-10-13 from the
documents linked; page numbers are the user guide's printed ones.

## 1. The dataset

NEON samples benthic macroinvertebrates (insects, crustaceans, worms, molluscs) at all 34 of its
aquatic sites, three times a year, with a sampler chosen by habitat (Surber, Hess, hand corer,
snag, kicknet, D-frame, petite ponar), and sends the samples to an external laboratory that
sorts, subsamples, identifies and counts them. The product is three main tables joined by
`sampleID`: `inv_fieldData` (one row per sample collected, with the sampler, habitat and the
benthic area it covered), `inv_persample` (laboratory quality metrics per sample) and
`inv_taxonomyProcessed` (the identifications, standardised and de-synonymised, one row per taxon
*and 1 mm size class* per sample). The expanded package adds `inv_taxonomyRaw` (the laboratory's
verbatim names) and `inv_identificationHistory` (determinations that were later changed).

Where to look:

- Product page, with the *Issue log* tab: https://data.neonscience.org/data-products/DP1.20120.001
- API record, where the issue log is `changeLogs` and the documents are `specs`: https://data.neonscience.org/api/v0/products/DP1.20120.001
- User guide (NEON_macroinvertebrate_userGuide_vF, 13 pages): https://data.neonscience.org/api/v0/documents/NEON_macroinvertebrate_userGuide_vF
- Quick start guide (NEON.QSG.DP1.20120.001v2): https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP1.20120.001v2
- Field protocol (NEON.DOC.003046vG): https://data.neonscience.org/api/v0/documents/NEON.DOC.003046vG
- Release DOIs: RELEASE-2026 [10.48443/hp56-s582](https://doi.org/10.48443/hp56-s582), RELEASE-2025 [10.48443/rmeq-8897](https://doi.org/10.48443/rmeq-8897), RELEASE-2024 [10.48443/je35-bc57](https://doi.org/10.48443/je35-bc57), back to RELEASE-2021 [10.48443/855x-0n27](https://doi.org/10.48443/855x-0n27)
- Papers tagged with the product in NEON's library (17 on 2026-10-13): https://www.zotero.org/groups/2665225/neon_publications/tags/DP1.20120.001
- NEON's own tutorial that computes density and richness from it: [aquatic-data-product-integration.R](https://github.com/NEONScience/NEON-Data-Skills/blob/main/tutorials/R/Aquatics/AIS-AOS-integration/aquatic-data-product-integration.R), and the older [01_working_with_NEON_macroinverts.R](https://github.com/NEONScience/NEON-Data-Skills/blob/main/tutorials/R/biodiversity/aquatic-biodiversity/01_working_with_NEON_macroinverts/01_working_with_NEON_macroinverts.Rmd)

The data themselves need a free NEON API token since June 2026; the catalogue, the documents and
the change log do not, which is why this example and the index can be reproduced without one.

## 2. What the stewards wrote down

The index's row for this product, from `uv run neon.py` on 2026-10-13:

| Papers | Changed | Fault | Gap | Other | Flagged | Unresolved | Sites | Docs |
|---|---|---|---|---|---|---|---|---|
| 17 | 11 | 0 | 3 | 0 | 2 | 0 | all | 7 |

All sixteen change-log entries, in full and with the kind the classifier assigned, are in
[`changelog.md`](changelog.md) beside this file (`uv run neon.py --product DP1.20120.001`).
In summary, with what a user has to do about each:

| Span | Sites | Kind | What happened | What a user has to do |
|---|---|---|---|---|
| 2014-07 to 2018-01 | all | changed | the laboratory did not use a standard taxonomic effort | treat identification depth before 2018 as not comparable with after; the user guide (p. 12) says the standard applies "after October 2018" and the standard's own file is dated 2019-07, so three dates disagree |
| 2018-11 to 2018-12 | all | changed | the laboratory began using the name *Neoleptophlebia* for animals previously called *Paraleptophlebia* | merge the two names, or richness gains a taxon at the boundary even in the de-synonymised table |
| 2014-07 to 2020-12 | 7 lakes | changed | near-shore points named `inlet` and `outlet` at seepage lakes with neither | map `inlet` to `littoral1`, `outlet` to `littoral2` |
| 2017-01 to 2022-10 | TOOK | changed | a sampling point published under the wrong name, `littoral1` for `littoral3` | nothing now, the records were edited; an older download disagrees with a newer one |
| 2014-07 to 2019-12 | all | flagged | `inv_fieldData` published in duplicate for all sites | nothing in RELEASE-2022 or later; de-duplicate anything earlier |
| 2012 to 2021-12 | all | flagged | species listed as threatened or sensitive by any state were published at a higher rank | nothing in RELEASE-2022 or later except in two domains; a species count from an earlier release is lower |
| 2012 to 2023-04 | HOPB | changed | the same, redone at site rather than domain granularity in one domain | a species count from before RELEASE-2024 at those sites is lower |
| 2012 to 2023-01 | all | changed | changes to past determinations were not tracked | from RELEASE-2024, read `inv_identificationHistory` to see what a name used to be |
| 2020-03 to 2021-12 | all | gap | COVID-19 reduced or cancelled sampling | missing bouts are `samplingImpractical` rows, not zeros |
| 2020-03 to 2022-12 | 2 sites | gap | quarantine at Toolik Field Station | the same |
| 2022-06 to 2022-10 | BLDE | gap | flooding closed the roads into Yellowstone | the same |
| 2021-07 to 2023-08 | all | changed | the identification laboratory changed | the stewards expect no effect; a user comparing across 2023 should check |
| 2014-07 to 2024-12 | all | changed | vial-location fields added to the taxonomy tables, `inv_pervial` retired, back-filled for all years | an older download lacks columns a newer one has |
| 2014-07 to 2026-01 | PRLA | changed | a sampling point moved closer to shore | samples at that point after 2026 are from a different place |
| 2014-07 to 2026-01 | all | changed (two entries) | the sampling windows were recalculated from NEON's own discharge and temperature data | bouts after 2026 fall in different months; seasonal comparisons across 2026 need care |

The classifier's keyword rules did well here: all eleven *changed* entries change what a column
means or what a download contains, the three *gap* entries are gaps, and the two *flagged* ones
are fixes applied in the data. A person would add two things the rules cannot: the sampling-window
entry is filed twice (the second has the first as its parent), and the laboratory-switch entry is
the kind a user should read and may then ignore.

## 3. A plausible question, and the silent errors

The question: *how have macroinvertebrate richness and density changed at Posey Creek (POSE,
Virginia) since sampling began in 2016?* It is the kind of question this product exists to
answer, every paper tagged with it asks something like it, and an agent given the three tables
and nothing else will answer it confidently. Where it goes wrong, each with where the correction
lives and whether anything in the data signals it:

1. **A row of `inv_taxonomyProcessed` is not an individual and not a taxon.** It is one taxon in
   one 1 mm size class, and the laboratory sometimes reports a size class twice, marked by a
   letter in `sizeCategory`, "and numbers should be summed" (user guide p. 8). A row count per
   sample counts size classes. *Signal in the data*: none; the column is called `sizeClass` and
   nothing says rows repeat.
2. **`estimatedTotalCount` is corrected for subsampling and not for area.** The laboratory sorts
   a sample until it has counted about 300 animals and scales up, so `estimatedTotalCount` is the
   whole sample's count, while `individualCount` is the subsample tally. But the guide is explicit
   that the count "is NOT corrected for benthic area" and that "all taxon records from a sample
   should be summed and divided by the benthicArea" from `inv_fieldData` (p. 8). The areas differ
   forty-fold by sampler (a hand core 0.006 m², a Surber 0.093 m², a kicknet 0.25 m²), so a sum of
   counts across samples compares a core with a kicknet. *Signal in the data*: `benthicArea` is a
   column in the other table, with no foreign-key hint that it divides anything.
3. **Richness before 2018 is not the same measurement as richness after.** The laboratory used
   no standard taxonomic effort until the stewards imposed one; after that, each group has a
   target rank (Collembola to genus, Enchytraeidae to family, Oribatida to suborder). A
   richness trend from 2016 partly measures the laboratory's effort. *Signal in the data*: none;
   only the change log and the guide's effort table say so, and their dates disagree by a year.
4. **A name split sits inside the series.** From November 2018 the laboratory called some
   *Paraleptophlebia* animals *Neoleptophlebia*, and the processed table carries both names on
   either side of the date. A per-year richness gains a genus at the boundary. *Signal in the
   data*: none; the table is described as de-synonymised, which is true of the standard's
   synonyms and not of this one.
5. **Coarse and fine rows of the same lineage count twice.** Immature or damaged specimens are
   recorded at family or order with `immatureSpecimen`, `indeterminateSpecies` or
   `sampleCondition` set (guide p. 10), so a distinct count of `scientificName` counts a family
   and a genus within it as two taxa. *Signal in the data*: the qualifier columns exist, which is
   a signal, but nothing says richness should exclude them, and NEON's own tutorials do not.
6. **A missing bout is a row, not an absence.** When sampling was impractical (dry, frozen,
   flood, a pandemic, a closed road) `inv_fieldData` has a row with `samplingImpractical` set and
   no children. Left in, it is a sample of zero animals. *Signal in the data*: the column is a
   flag, and this is the one error on the list an agent can avoid by reading column names.
7. **Which release matters.** Field data for 2014 to 2019 were duplicated before RELEASE-2022;
   state-listed species were published at a higher rank before RELEASE-2022 (and before
   RELEASE-2024 at some sites); past determinations were overwritten without record before
   RELEASE-2024; provisional data are revised on a rolling basis. Two downloads of "the same"
   product give different richness. *Signal in the data*: the release name is in the download's
   file names and nowhere in the rows.
8. **The effort columns are not enough on their own.** `samplerType`, `habitatType` and
   `benthicArea` normalise for area, but the kicknet is "semi-quantitative" (protocol), nothing
   records a D-frame sweep's length, and samplers changed with protocol revisions in 2018. A
   density trend across a sampler change is partly a sampler trend. *Signal in the data*: the
   sampler is named per row; the caveat is in the protocol.

Two errors on this list, 1 and 2, are in the user guide and in no change log, which matters for
the index below. One, 6, is in the data. The rest are in the change log, the guide or the
protocol, and the stewards' tutorial is the place to check how much of this even an expert reader
applies: NEON's integration tutorial sums size classes correctly for density but, for richness
and the diversity indices, keeps only the first size-class row per taxon with `distinct()` before
pivoting, so its Shannon and Simpson values are computed on truncated counts; and neither tutorial
excludes the coarse-rank rows of error 5, merges the synonym of error 4, or normalises across
sampler types. This is not a complaint about the tutorial. It is the point: the corrections are
scattered across four documents and a change log, and a careful human with the documents open
still misses some, so an agent without them will miss more and say nothing.

## 4. What the model-free index saw, and what it missed

The index ranks this product high because many papers use it and eleven of its sixteen entries
change the meaning of a column or the contents of a download. That is the right answer for
errors 3, 4, 7 and the renamed points, and the entries themselves, read as a list, are most of
the recipe a user needs for them.

It cannot see errors 1, 2, 5 and 8. They are properties of the data model, written once in the
user guide and never in a change log because nothing ever changed: `estimatedTotalCount` was
always per sample and never per square metre. A change log records what moved; the count
semantics never moved. So the index under-reports exactly the errors that are easiest to make,
and a product with a perfect change log and a subtle data model would score as ready. The
documents count is a weak stand-in (seven here), and reading the guide is the real one. That is
the honest limit of the model-free index and the reason the probes exist.

## 5. What the LLM probes would find, and what that would tell us

The three probes, written for this product. None has been run; what follows is the design and
the reading of each outcome, so that a result, when there is one, says something.

**Flag honoured unprompted.** Give the agent the three tables for POSE and the question above,
with no documentation. Does it drop the `samplingImpractical` rows? One bit. The expected result
is yes for most current models, because the column name is self-describing; a no would say the
agent does not read column names before aggregating, which is worth knowing about the agent and
nothing about the dataset.

**With and without the user guide.** The same question twice: once with the tables alone, once
with the user guide and quick start guide in context. Diff the two answers, number by number and
step by step. The expected divergence is concentrated at errors 1 and 2: the without-guide answer
counts rows or sums `individualCount`, and reports density per sample rather than per square
metre; the with-guide answer sums `estimatedTotalCount` over size classes and divides by
`benthicArea`. The 2018 effort boundary (error 3) should appear in the with-guide answer as a
caveat or a split series, and in the without-guide answer not at all. Where the two answers agree,
the semantics were recoverable from the data; where they differ, the documentation carried them.
No ground truth is needed, which is why this probe scales to products nobody has hand-checked.

**Seeded corruptions.** Plant three errors in the inputs and ask the same question with the
guide in context: multiply `benthicArea` by ten for one sampler type; rename every
*Neoleptophlebia* row after 2018 back to *Paraleptophlebia* on one side of a bout and not the
other; duplicate one bout's `inv_fieldData` rows as the 2021 publishing error did. Score whether
the answer changes and whether the agent says why. This is the measurement with a number: a
silent-error rate, per corruption, per model.

What each outcome would tell us, as a grid over the second probe, for one error:

| | Right with the guide | Wrong with the guide |
|---|---|---|
| **Right without it** | the semantics are in the data (error 6); low priority for curation | an unlikely cell; the guide misled, which is a documentation bug worth reporting |
| **Wrong without it** | the documentation carries the semantics (errors 1 to 4); a machine-readable recipe or richer column metadata would move this error to the top row | either the guide is insufficient (error 8: the kicknet caveat is in the protocol, not the guide) or the agent cannot apply what it read; distinguish the two by adding the protocol, and if it stays wrong, the fix is a constraint on the agent, not more documentation |

The bottom-left cell is where a transformation recipe pays for itself, and for this product the
expectation is that errors 1 to 4 land there. The bottom-right cell is the one that argues for
constraining what an agent may do to data rather than documenting more.

Three caveats a reviewer should hold onto. The results are per model and per prompt, so a probe
result is a sentence with a model name and a date in it, never a property of the dataset alone;
running two or three models and reporting the spread is the minimum. The without-guide run is not
a fair test of the agent, since nobody should analyse this product without the guide, and it is
not meant to be: it is a test of where the semantics live. And a corruption the agent catches
tells us the agent read something, not that it would have caught the real error; the real
errors are the ones in section 3, and the seeded ones are stand-ins chosen to be scorable.

## 6. What this tells a steward, and what it does not

For NEON, or any repository with the same shape of records: the sixteen entries are a good
change log, and the index rewards them. What would make most of section 3 machine-checkable is
small: an *affected columns* field on each change-log entry, so that `sizeCategory`,
`scientificName`, `namedLocation` are named by the entries that change them; and a column-level
note on `estimatedTotalCount` saying "per sample; divide by `inv_fieldData.benthicArea`", which is
the one sentence from the user guide that an agent most needs and least often finds. Croissant's
per-field descriptions are one place such a note could live; a machine-readable recipe (sum over
size classes, divide by area, merge these synonyms, exclude these qualifiers) is the fuller
answer.

The contrast product is water quality (DP1.20288.001), the continuous sonde data at the same 34
sites: 292 entries, of which 183 are flagged and most of the rest are unflagged sensor faults.
There the burden is a flag column the agent must honour, and the recipe is one line. The two
products at the same sites show the two populations the index has to tell apart, and why a raw
entry count could not.

What this does not say: that NEON's data are hard to use, as data go. They are among the best
documented in ecology, which is why the semantics can be found at all; a repository without a
change log or a user guide would score as ready and be worse. It does not say the keyword
classifier is right in general: it was right on these sixteen entries and will be wrong on
others, and a model over the entry text is the obvious upgrade. And it does not say anything
about the agents yet: the probes are designed, not run, and until they run the grid above is a
reading guide, not a result.

## 7. Reproduce

```sh
uv run neon.py --product DP1.20120.001 > examples/NEON/changelog.md   # one GET, seconds
uv run neon.py > readiness.md                                          # the whole index, a few minutes
```

Both need no token. The documents linked in section 1 are the sources for every statement about
the data model, and the product's `changeLogs` array is the source for section 2.
