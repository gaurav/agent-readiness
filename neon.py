# /// script
# requires-python = ">=3.11"
# ///
"""Readiness index for NEON data products: how much a user has to know, times how much it is used.

    uv run neon.py > readiness.md          # the table, Markdown, to stdout
    uv run neon.py --self-check            # same run, then asserts on the result

For every product in NEON's data API this reads the change log its stewards have filed (entries,
how many are unresolved, the sites and dates they affect) and the documents a user is expected to
read, and counts the papers tagged with the product code in NEON's Zotero publications library
(group 2665225, whose tags carry item counts). The table is sorted by papers times change-log
entries: a proxy for where the semantics have moved under old code and many people are relying on
it. It is a proxy only; see README.md for what it stands in for and what it misses.

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
        rows.append({
            "code": code, "name": p["productName"], "status": p["productStatus"],
            "papers": papers.get(code, 0),
            "logs": len(logs),
            "unresolved": sum(1 for c in logs if not c.get("resolvedDate")),
            "sites": "all" if "All" in sites else str(len(sites)),
            # many logs start on 2010-01-01 or 2012-01-01, before the site existed: a default, not a date
            "since": min((c["dateRangeStart"][:10] for c in logs if c.get("dateRangeStart")), default=""),
            "docs": len(d.get("specs") or []),
        })
    # ponytail: papers x change-log entries is a naive score; weight by unresolved or by months if it misleads
    rows.sort(key=lambda r: (-(r["papers"] * r["logs"]), -r["logs"], -r["papers"], r["code"]))
    return rows


def render(rows, papers, malformed):
    out = [f"# NEON readiness index, generated {datetime.date.today()} by neon.py from "
           "https://github.com/gaurav/agent-readiness", "",
           f"{len(rows)} products; {sum(1 for r in rows if r['papers'])} have at least one paper tagged with their "
           f"code in NEON's Zotero library ({sum(papers.values())} product tags over {len(papers)} codes; "
           f"{len(malformed)} malformed product tags ignored: {', '.join(sorted(malformed))}); "
           f"{sum(1 for r in rows if r['logs'])} have change-log entries.", "",
           "Sorted by papers × change-log entries. *Sites* is the distinct sites a change log names, or *all*; "
           "*since* is the earliest date a change log affects (often a placeholder); *docs* is the product's "
           "user guide, protocol and quick-start files.", "",
           "| Code | Name | Status | Papers | Change logs | Unresolved | Sites | Since | Docs |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['code']} | {r['name']} | {r['status']} | {r['papers']} | {r['logs']} | {r['unresolved']} | "
                   f"{r['sites']} | {r['since']} | {r['docs']} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    papers, malformed = papers_per_product()
    rows = product_rows(papers)
    text = render(rows, papers, malformed)
    if "--self-check" in sys.argv:
        by_code = {r["code"]: r for r in rows}
        assert len(rows) > 150, len(rows)
        assert by_code["DP1.20120.001"]["logs"] > 0, "macroinvertebrates should carry change-log entries"
        assert by_code["DP1.20120.001"]["papers"] > 0, "macroinvertebrates should have tagged papers"
        assert text.count("\n|") == len(rows) + 2, "one table row per product plus header and rule"
        print(f"self-check ok: {len(rows)} products, top {rows[0]['code']} {rows[0]['name']}", file=sys.stderr)
    else:
        sys.stdout.write(text)
