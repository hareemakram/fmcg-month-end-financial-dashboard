"""Generates docs/report-layout-spec.md and docs/data-dictionary.md from the definitions in build_pbip.py."""
import os
import build_pbip as B

PURPOSE = {
    "p01_ExecutiveSummary": "One-screen answer to *how did we close the month?* Five headline KPIs with variance subtitles, the actual vs forecast vs budget trend, the YTD budget bridge, and category, region and channel breakdowns.",
    "p02_VarianceAnalysis": "Explains *where and why* actuals differ from plan: monthly variance bars, forecast accuracy trend against target, and a category › brand › SKU variance matrix with region and channel splits.",
    "p03_PeriodKPIs": "Time-intelligence view: QTD, YTD and rolling-12-month KPIs, the cumulative YTD race against budget, forecast and prior year, quarterly YoY comparison, and a Year › Quarter › Month KPI table.",
    "p04_ProductRegion": "Drilldown for commercial teams: portfolio matrix with drill, SKU growth vs margin scatter, region vs prior year, a region × channel-group grid and a customer ranking.",
}


def fields(v):
    q = v["visual"].get("query", {}).get("queryState", {})
    parts = []
    for role, ps in q.items():
        names = []
        for p in ps["projections"]:
            f = p["field"]
            if "Measure" in f:
                n = f"[{f['Measure']['Property']}]"
            else:
                n = f"{f['Column']['Expression']['SourceRef']['Entity']}[{f['Column']['Property']}]"
            if p.get("displayName"):
                n += f" as “{p['displayName']}”"
            names.append(n)
        parts.append(f"**{role}:** " + ", ".join(names))
    return "<br>".join(parts)


def title(v):
    t = v["visual"].get("visualContainerObjects", {}).get("title", [{}])[0].get("properties", {}).get("text")
    return t["expr"]["Literal"]["Value"].strip("'") if t else ""


def notes(v):
    n = []
    o = v["visual"].get("objects", {})
    for f in v.get("filterConfig", {}).get("filters", []):
        n.append("Visual filter: " + {"fTrendWindow": "Month Offset −12 … +2", "fVarWindow": "Month Offset −12 … 0", "fAccWindow": "Month Offset −12 … 0",
                                      "fGmWindow": "Month Offset −12 … 0", "fCurrentYear": "Year Offset = 0"}.get(f["name"], f["name"]))
    def measure_refs(x):
        out = []
        if isinstance(x, dict):
            if "Measure" in x and isinstance(x["Measure"], dict) and "Property" in x["Measure"]:
                out.append(x["Measure"]["Property"])
            for y in x.values():
                out += measure_refs(y)
        elif isinstance(x, list):
            for y in x:
                out += measure_refs(y)
        return out
    cf = sorted(set(measure_refs(o)))
    if cf:
        n.append("Conditional colour from " + ", ".join(f"[{m}]" for m in cf))
    if "sortDefinition" in v["visual"].get("query", {}):
        s = v["visual"]["query"]["sortDefinition"]["sort"][0]
        f = s["field"]
        nm = f.get("Measure", f.get("Column"))["Property"]
        n.append(f"Sorted by {nm} ({s['direction'].lower()})")
    return "<br>".join(n)


pages = B.build_pages()
md = ["# Report layout spec", "",
      "Canvas: **1280 × 720**, Fit to page. Theme: `theme/Aurora_FMCG_Theme.json` (page `#F4F3EF`, white cards with a 10 px radius, a hairline border and a soft shadow, Segoe UI).",
      "This spec is generated from the report definition in `pbip/`, so positions and fields match the PBIP exactly. Positions are x, y, width, height in px.", "",
      "## Shared on every page", "",
      "| Element | Position | Content |", "|---|---|---|",
      "| Title block (text box) | 8, 6, 470, 60 | Page title in Segoe UI Semibold 20 pt, subtitle in 10 pt muted |",
      "| 5 dropdown slicers | from x 488, y 12, each 106 × 50 | Date[Year] (single select), Date[Month] (single select), Region[Region], Channel[Channel], Product[Category] |",
      "| Close period pill (card) | 1060, 12, 204, 50 | [Reporting Period Label] in white on navy `#0F1B2D` |",
      "| Footer (card) | 1000, 700, 270, 20 | [Data As Of Label] |",
      "| KPI tiles | y 76, height 106, equal widths across 1248 px with 12 px gaps | A card showing the value with the KPI title, plus a borderless card overlaid at the bottom showing the subtitle measure, coloured by a `Color …` measure |", "",
      "Colour roles: **Actual** blue `#2A78D6` (solid, 3 px), **Forecast** orange `#EB6834` (dashed), **Budget** aqua `#1BAF7A` (dotted), **Prior year** grey `#A9A7A0`. Favourable/unfavourable use green `#0CA30C`/`#006300` and red `#D03B3B`, always paired with ▲/▼ or a sign, so colour is never the only cue.", ""]
for p in pages:
    md += [f"## {p.display}", "", PURPOSE[p.name], "", "| # | Visual | Type | Position | Fields | Notes |", "|---|---|---|---|---|---|"]
    i = 0
    for v in p.visuals:
        if v["name"] in ("hdrTitle", "hdrPeriod", "ftrAsOf") or v["name"].startswith("sl"):
            continue
        i += 1
        pos = v["position"]
        t = title(v) or ("KPI subtitle" if v["name"].endswith("Label") else "")
        md.append(f"| {i} | {t} | `{v['visual']['visualType']}` | {pos['x']}, {pos['y']}, {pos['width']}, {pos['height']} | {fields(v)} | {notes(v)} |")
    md.append("")
md += ["## Interaction notes", "",
       "* All visuals cross-filter each other (default interactions). Slicers sync by field name across pages if you enable *View › Sync slicers*.",
       "* Matrices are built with Category › Brand › Product (or Year › Quarter › Month) on Rows. Use the drill buttons or *Expand all* to go deeper.",
       "* Choosing a Year without a Month moves the anchor to that year's last closed month. Choosing a Month too shows that exact close.",
       "* Trend visuals use the `Month Offset` window filters, so they always show the latest 13 closed months without manual date maintenance.", ""]
open(os.path.join(B.ROOT, "docs", "report-layout-spec.md"), "w", encoding="utf-8").write("\n".join(md))

# ---------------- data dictionary
grain = {"Date": "One row per day, 1 Jan 2024 – 31 Dec 2026 (generated in Power Query)", "Product": "One row per SKU (46)", "Customer": "One row per customer (78)",
         "Region": "One row per sales region (6)", "Channel": "One row per channel (5)", "Fact Sales": "One row per sales order line (174,800), Jan 2024 – Oct 2026",
         "Fact Forecast": "Month × SKU × region × channel (45,618 rows), Jan 2024 – Dec 2026, latest rolling forecast and budget side by side",
         "Variance Bridge": "3 rows: Budget, Volume & Mix, Price & Discount (disconnected helper for the waterfall)", "_Measures": "Empty table that holds the 182 measures"}
dd = ["# Data dictionary", "", "## Relationships", "", "All are one-to-many with single-direction filtering from the dimension to the fact.", "",
      "| From (many) | To (one) |", "|---|---|"]
dd += [f"| `{ft}[{fc}]` | `{tt}[{tc}]` |" for (ft, fc, tt, tc) in B.RELATIONSHIPS]
dd += [""]
for t, s in B.TABLES.items():
    dd += [f"## {t}", "", grain[t], "", "| Column | Type | Notes |", "|---|---|---|"]
    for (c, dt, fl) in s["columns"]:
        n = []
        if fl.get("hidden"): n.append("hidden")
        if fl.get("key"): n.append("date table key")
        if fl.get("sortBy"): n.append(f"sorted by {fl['sortBy']}")
        dd.append(f"| {c} | {dt} | {', '.join(n)} |")
    for (c, dt, e, d) in s.get("calculated", []):
        dd.append(f"| {c} | {dt} (calculated) | {d} |")
    for (c, dt, e, d) in s.get("calculated", []):
        dd += ["", f"**{c}**", "", "```dax", f"{c} =", e, "```"]
    for (h, lv) in s.get("hierarchies", []):
        dd += ["", f"Hierarchy **{h}**: " + " › ".join(lv)]
    dd.append("")
open(os.path.join(B.ROOT, "docs", "data-dictionary.md"), "w", encoding="utf-8").write("\n".join(dd))
print("docs written")
