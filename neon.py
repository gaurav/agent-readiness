# /// script
# requires-python = ">=3.11"
# ///
"""Readiness index for NEON data products: how much a user has to know, times how much it is used.

    uv run neon.py > readiness.md          # the table, Markdown, to stdout
    uv run neon.py --product DP1.20120.001 # one product's change log, classified, one GET
    uv run neon.py --self-check            # same run, then asserts on the result

For every product in NEON's data API this reads the change log its stewards have filed and sorts
each entry by what a user has to do about it: `flagged` (the fix is already in the product's
quality-flag columns: a clogged gauge, a drifting sensor), `changed` (the data or its meaning
changed: a taxonomic synonym, a renamed sampling point, a reduced design, a reprocessed release),
`gap` (sampling did not happen: a pandemic, a closed road), or `other`. It also counts the
documents a user is expected to read and the papers tagged with the product code in NEON's Zotero
publications library (group 2665225, whose tags carry item counts). The table is sorted by papers
times `changed` entries, which is where many people rely on a product whose meaning moved without
a flag to say so; the `changed` entries themselves follow the table, as the seed list for probes
and the draft of a recipe. See README.md for what this stands in for and what it misses.

NEON is the testbed, not the target: its API, change logs and tagged publication library make
the index computable in an afternoon. The method is meant for any repository that keeps the
equivalent records.

About 230 anonymous GETs at one a second, stdlib only, so `uv run` needs nothing installed.
"""
import datetime
import json
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://data.neonscience.org/api/v0"
ZOTERO = "https://api.zotero.org/groups/2665225"  # NEON's publications library, tagged by product code
PRODUCT = re.compile(r"^DP\d\.\d{5}\.\d{3}$")

# ponytail: keyword rules, in priority order; a model over the entry text is the upgrade if these mislead
GAP = re.compile(r"covid|pandemic|quarantin|halt|not (be )?sampled|no sampling|closed|flood|fire|hurricane|"
                 r"suspend|cancel|operations ended", re.I)
FLAGGED = re.compile(r"flag|offline|removed from|set to (null|na)|redact|data (were|was|have been) removed", re.I)
CHANGED = re.compile(r"taxonom|synonym|effort|renam|named|called|format|field|reprocess|republish|design|method|"
                     r"protocol|unit|duplicat|obfuscat|interval|reduc|increas|discontinu|convert|identif|relocat|"
                     r"algorithm|atbd|equation|table|column|swap", re.I)
FAULT = re.compile(r"sensor|sonde|probe|drift|clog|calibrat|power|battery|buried|foul|wiper|transducer|gauge|"
                   r"malfunction|logger|cable|firmware", re.I)


def kind(entry):
    """What a user has to do about a change-log entry, from its text.

    gap: sampling did not happen; flagged: the fix is in the quality-flag columns; changed: the data or its
    meaning changed and only the entry says so; fault: a sensor fault with no flag mentioned, an unflagged
    bad span; other.
    """
    issue, resolution = entry.get("issue") or "", entry.get("resolution") or ""
    text = issue + " " + resolution
    if GAP.search(issue):
        return "gap"
    if FLAGGED.search(resolution):
        return "flagged"
    if CHANGED.search(text):
        return "changed"
    if FAULT.search(text):
        return "fault"
    return "other"


def get(url):
    """One GET, one second apart, honouring Retry-After once."""
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as r:
                body = json.load(r)
                time.sleep(1)
                return body
        except urllib.error.HTTPError as e:
            if attempt == 2 or e.code not in (429, 503):
                raise
            time.sleep(int(e.headers.get("Retry-After", "10")))


def papers_per_product():
    """Zotero's /tags carries numItems per tag, so no per-product query is needed."""
    papers, malformed, start = {}, [], 0
    while True:
        page = get(f"{ZOTERO}/tags?limit=100&start={start}")
        for t in page:
            tag = t["tag"]
            if tag.startswith("DP"):
                if PRODUCT.match(tag):
                    papers[tag] = t["meta"]["numItems"]
                else:
                    malformed.append(tag)
        if len(page) < 100:
            return papers, malformed
        start += 100


def product_rows(papers):
    rows = []
    for p in get(f"{API}/products")["data"]:  # NEON wraps its body in data; Zotero does not
        code = p["productCode"]
        d = get(f"{API}/products/{code}")["data"]
        logs = d.get("changeLogs") or []
        sites = set()
        for c in logs:
            sites.update(s.strip() for s in (c.get("locationAffected") or "").split(",") if s.strip())
        kinds = [kind(c) for c in logs]
        rows.append({
            "code": code, "name": p["productName"], "status": p["productStatus"],
            "papers": papers.get(code, 0),
            "logs": len(logs),
            "changed": kinds.count("changed"), "fault": kinds.count("fault"), "flagged": kinds.count("flagged"),
            "gap": kinds.count("gap"), "other": kinds.count("other"),
            "unflagged": len(logs) - kinds.count("flagged"),
            "entries": [(k, c) for c, k in zip(logs, kinds) if k in ("changed", "fault")],
            "unresolved": sum(1 for c in logs if not c.get("resolvedDate")),
            "sites": "all" if "All" in sites else str(len(sites)),
            # many logs start on 2010-01-01 or 2012-01-01, before the site existed: a default, not a date
            "since": min((c["dateRangeStart"][:10] for c in logs if c.get("dateRangeStart")), default=""),
            "docs": len(d.get("specs") or []),
        })
    # ponytail: papers x unflagged entries is a naive score; weight by kind or by span if it misleads
    rows.sort(key=lambda r: (-(r["papers"] * r["unflagged"]), -r["unflagged"], -r["papers"], r["code"]))
    return rows


def render(rows, papers, malformed):
    out = [f"# NEON readiness index, generated {datetime.date.today()} by neon.py from "
           "https://github.com/gaurav/agent-readiness", "",
           f"{len(rows)} products; {sum(1 for r in rows if r['papers'])} have at least one paper tagged with their "
           f"code in NEON's Zotero library ({sum(papers.values())} product tags over {len(papers)} codes; "
           f"{len(malformed)} malformed product tags ignored: {', '.join(sorted(malformed))}); "
           f"{sum(1 for r in rows if r['logs'])} have change-log entries.", "",
           "Sorted by papers × entries not handled by a flag. Each change-log entry is sorted by what a user "
           "has to do about it: *flagged*, the fix is in the quality-flag columns; *changed*, the data or its "
           "meaning changed and only the entry says so; *fault*, a sensor fault with no flag mentioned, so an "
           "unflagged bad span; *gap*, sampling did not happen; *other*. *Sites* is the distinct sites the log "
           "names, or *all*; *since* is the earliest date it affects (often a placeholder); *docs* is the "
           "product's user guide, protocol and quick-start files.", "",
           "| Code | Name | Status | Papers | Changed | Fault | Gap | Other | Flagged | Unresolved | Sites | Since | Docs |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['code']} | {r['name']} | {r['status']} | {r['papers']} | {r['changed']} | {r['fault']} | "
                   f"{r['gap']} | {r['other']} | {r['flagged']} | {r['unresolved']} | {r['sites']} | {r['since']} | "
                   f"{r['docs']} |")
    out += ["", "## Entries that changed the data or its meaning, or left an unflagged fault", "",
            "For products with at least one tagged paper, every *changed* and *fault* entry: the span and sites it "
            "affects, what was wrong, and what was done. Each is a question an agent should answer differently on "
            "either side of the span, and the *changed* ones together are the draft of the product's recipe.", ""]
    for r in rows:
        if not r["papers"] or not r["entries"]:
            continue
        out += [f"### {r['code']} {r['name']} ({r['papers']} papers, {r['changed']} changed, {r['fault']} fault)", ""]
        out += [entry_line(k, c) for k, c in r["entries"]] + [""]
    return "\n".join(out)


def entry_line(k, c):
    span = f"{(c.get('dateRangeStart') or '')[:10]} to {(c.get('dateRangeEnd') or '')[:10]}"
    where = c.get("locationAffected") or ""
    issue = " ".join((c.get("issue") or "").split())
    fix = " ".join((c.get("resolution") or "").split())
    return f"- *{k}*, **{span}**, {where}: {issue} **Resolution:** {fix}"


def product_changelog(code):
    """One product's change log, every entry with its kind, as Markdown: one GET, no Zotero."""
    d = get(f"{API}/products/{code}")["data"]
    logs = d.get("changeLogs") or []
    out = [f"# {code} {d['productName']}: change log, {len(logs)} entries, read {datetime.date.today()} by neon.py "
           f"from https://github.com/gaurav/agent-readiness", "",
           f"Source: https://data.neonscience.org/api/v0/products/{code} (`changeLogs`); the same entries are the "
           f"issue log on https://data.neonscience.org/data-products/{code}. Each is prefixed with the kind the "
           "classifier assigns: flagged, changed, fault, gap or other. Entries are in the API's order.", ""]
    out += [entry_line(kind(c), c) for c in logs]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    if "--product" in sys.argv:
        sys.stdout.write(product_changelog(sys.argv[sys.argv.index("--product") + 1]))
        sys.exit()
    papers, malformed = papers_per_product()
    rows = product_rows(papers)
    text = render(rows, papers, malformed)
    if "--self-check" in sys.argv:
        by_code = {r["code"]: r for r in rows}
        assert len(rows) > 150, len(rows)
        assert by_code["DP1.20120.001"]["logs"] > 0, "macroinvertebrates should carry change-log entries"
        assert by_code["DP1.20120.001"]["papers"] > 0, "macroinvertebrates should have tagged papers"
        assert by_code["DP1.20120.001"]["changed"] > 0, "the synonymy and effort entries should classify as changed"
        assert by_code["DP1.00006.001"]["flagged"] > by_code["DP1.00006.001"]["changed"], "precipitation is mostly flagged"
        assert kind({"issue": "Sensor clogged", "resolution": "Applied manual flagging."}) == "flagged"
        assert kind({"issue": "Taxonomic synonomy", "resolution": "began using the scientificName X"}) == "changed"
        assert kind({"issue": "Safety measures during the COVID-19 pandemic", "resolution": "Sampling reduced."}) == "gap"
        assert kind({"issue": "Dissolved Oxygen sensor is drifting.", "resolution": "Sensor was cleaned."}) == "fault"
        one = product_changelog("DP1.20120.001")
        assert one.count("\n- *") == by_code["DP1.20120.001"]["logs"], "--product lists one line per entry"
        print(f"self-check ok: {len(rows)} products, top {rows[0]['code']} {rows[0]['name']}", file=sys.stderr)
    else:
        sys.stdout.write(text)
