# agent-readiness

Does a dataset carry the semantics a coding agent needs, where the agent will find them?

A coding agent handed a public dataset and a plausible question will often produce a confident
answer that is silently wrong: a count column summed when it is really an estimate over a
subsample, a flagged sensor outage averaged into a daily mean, a detection limit read as a
measurement, a survey count compared across sites without the effort that sits in a second table.
None of these raises an error. In every case the schema reads as simple and the correction lives
somewhere else, usually a user guide or a change log the agent never opened. This repository is
for measuring that gap, dataset by dataset, so that curation effort and documentation can go where
an agent most needs them.

## What it measures

Two kinds of measurement, one built and one not.

**A readiness index, model-free (built).** For each dataset in a repository, what its stewards have
written down that the schema does not say, and how many people rely on it. The source is the
change log the stewards keep: each entry says what went wrong, for which sites and dates, and
what was done about it. The index reads every entry and sorts it by what a user has to *do*
about it:

| Kind | What the entry says | What a user has to do |
|---|---|---|
| *flagged* | a fault whose resolution was to flag the affected rows | honour the quality-flag column; nothing to read |
| *changed* | the data or its meaning changed: a taxonomic synonym adopted, a sampling point renamed, a design reduced, a release reprocessed, an algorithm corrected | read the entry; the correction is nowhere in the data |
| *fault* | a sensor fault with no flag mentioned: a probe calibrated ten times too high, a sonde drifting until it was cleaned | treat the span as suspect; nothing in the data says so |
| *gap* | sampling did not happen: a pandemic, a flooded road, a site closed | know that absence is not zero |
| *other* | the rest | read it |

The sort key is papers times entries not handled by a flag. A count of all entries, which is
where this started, measures how observable a product's history is rather than how hard it is to
use: a rain gauge with five hundred flagged clogs is handled by one filter, and a repository that
keeps no change log would score as ready, which is backwards. The classification is keyword rules
over the entry text and will misfile some entries; the table carries every kind as a column so
a reader can re-sort, and the rules are the first thing to improve.

The entries themselves are the index's real product. Each *changed* or *fault* entry, with its
span and sites, is a question an agent should answer differently on either side of the span,
which makes it a ready-made probe with no corruption to invent; and the *changed* entries of a
product, read together, are most of the transformation recipe that product needs and does not
publish: map these synonyms, drop or flag the years before the effort was standardised, rename
these points. The table lists them, per product, after the ranking.

**Probes, run with an LLM agent (next).** The measurement the index stands in for:

- *Flag honoured unprompted*: given the data and a question, does the agent filter on the
  dataset's quality-flag column without being told? One bit per dataset, minutes each.
- *With and without documentation*: the same task twice, once with the user guide in context and
  once without; the diff of the two answers locates where the documentation carries semantics.
  No ground truth needed.
- *Seeded corruptions*: known errors planted in the inputs (a unit left unconverted, a detection
  limit as a value, a flagged span unflagged) against a known-good result; the silent-error rate
  with a number.

The probes are LLM-specific by construction, and their results will depend on the model and the
prompt, which is why the model-free index comes first and why the probe results will always say
which model ran them.

## NEON is the testbed, not the target

The first index is over the [National Ecological Observatory Network](https://www.neonscience.org/)'s
202 data products, because NEON makes it computable in an afternoon: an anonymous API whose
product records carry change logs with dates, sites, issue and resolution, and document lists,
and a [Zotero library](https://www.zotero.org/groups/2665225/neon_publications) of publications
tagged by product code. NEON's change logs are a sign of stewardship, not of trouble: a product
with many entries is one whose stewards wrote down what they found, and the index rewards that
by turning the entries into probes and recipe drafts. A repository with no change log is not more
ready, only less observable, and its entries would have to be recovered some other way (release
diffs, user forums, the cleaning packages its community has written). The method is meant for any repository
that keeps the equivalent records, and the second source is what will make that true. The
candidates: [GBIF](https://www.gbif.org/), whose dataset DOIs have tracked citations and whose
occurrence records carry per-record issue flags, and the
[Environmental Data Initiative](https://edirepository.org/), whose data packages carry revisions.

## Relation to the FAIR evaluation tools

The FAIR assessment tools score whether a dataset's *metadata record* is findable, accessible,
interoperable and reusable, at the level of the identifier, the landing page and the metadata
exposed there. This tool scores something they do not look at: whether the *data's semantics*
reach the point of use. The two are complementary, and each could carry the other's score as a
column. Facts below read from each tool's own site and repository on 2026-10-13.

| Tool | Assesses | Interface and input | Reads the data or its documentation? |
|---|---|---|---|
| [F-UJI](https://www.f-uji.net/) (PANGAEA / FAIRsFAIR, now FAIR-IMPACT; v4.0.1, 2026-09) | the FAIRsFAIR data-object metrics (sixteen or so, F1 to R1.3) over identifier, landing page and embedded or harvested metadata | web UI; REST `POST /fuji/api/v1/evaluate` with a PID or URL; Docker; R client | metadata; a file is Tika-sniffed for format and size when the metadata links one; never the documentation |
| [FAIR-Checker](https://fair-checker.france-bioinformatique.fr/) (IFB; v1.3.4, 2026-09) | twelve metrics named after FAIR sub-principles, plus Bioschemas profile validation, over the metadata extracted from a URL | web UI; REST `GET /api/check/metrics_all?url=` | metadata only |
| [FAIRshake](https://fairshake.cloud/) (Ma'ayan Lab, NIH CFDE; quiet since 2025) | user-defined rubrics, the featured one being the FAIR Metrics; any digital object | web UI, browser extension; REST API for records and rubrics; automated checks run from your own Python | rubric answers by people, or automated checks on metadata; not the data |
| [FAIR Evaluator](https://w3id.org/FAIR_Evaluator) (FAIR Metrics Group; running, Gen2 indicators marked deprecated in the metrics repository) | maturity-indicator tests, one per FAIR sub-principle, grouped in collections, over a GUID and the metadata it resolves to | web UI; REST `POST /collections/{id}/evaluate` | metadata only |

Also alive: [FAIR EVA](https://github.com/EOSC-synergy/FAIR_eva) (RDA indicators over
institutional repositories, REST API) and the
[ARDC self-assessment](https://ardc.edu.au/resource/fair-data-self-assessment-tool/) (a
questionnaire). None of these reads a user guide, and none asks whether a column means what it
says. That is the gap this tool is for.

How the two could connect:

- A FAIR score per dataset is one API call to F-UJI, FAIR-Checker or the Evaluator, and a column
  this index could carry, so a reader can see whether well-described metadata and recoverable
  semantics go together (the working hypothesis is that they often do not).
- A readiness probe is a metric their rubrics could adopt: FAIRshake's rubrics and the FAIR
  Metrics collections are both open to new tests, and a test that runs an agent is only a test
  with a slower executor.
- The nearer neighbours are the AI-readiness efforts rather than the FAIR tools. NIH Bridge2AI's
  [AI-readiness criteria](https://pmc.ncbi.nlm.nih.gov/articles/PMC11526931/) require a linked
  human-readable datasheet and a machine-readable data dictionary, which is the closest *stated*
  requirement to what the probes test, but as a checklist over metadata packaging rather than a
  test of whether an agent recovers a caveat. [AIDRIN](https://pypi.org/project/aidrin/) (Ohio
  State; 2026.9) reads the data itself and scores statistical readiness across six dimensions,
  with an MCP server for agents; it is the nearest live tool and measures a different thing
  (distribution, bias, structure) from documented semantics. MLCommons'
  [Croissant](https://mlcommons.org/croissant/) format is where per-column semantics could be
  published; it has no score.

## Running

```sh
uv run neon.py > readiness.md     # the ranking, then the changed and fault entries per product; about 230 GETs at one a second
uv run neon.py --self-check       # the same run, then asserts on the result and on the classifier
```

Standard library only, so `uv run` needs nothing installed; the script also runs from its raw
GitHub URL. No token: the NEON catalogue endpoints and Zotero's group API answer anonymously.

## Status

A first index over one repository, with its change-log entries classified by keyword rules, and
the probes designed but not built. Next, in order: run the *changed* entries of one product as
probes (does the agent's answer differ across the span?); a second source (GBIF or EDI) so the
index is shown to be a method; a better classifier if the keyword rules misfile enough to matter.
Issues and pull requests are welcome, in particular on the classification rules and on
repositories whose records would let the index run.

## Licence

MIT.
