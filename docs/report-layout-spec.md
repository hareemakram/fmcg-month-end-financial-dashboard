# Report layout spec

Canvas: **1280 × 720**, Fit to page. Theme: `theme/Aurora_FMCG_Theme.json` (page `#F4F3EF`, white cards with a 10 px radius, a hairline border and a soft shadow, Segoe UI).
This spec is generated from the report definition in `pbip/`, so positions and fields match the PBIP exactly. Positions are x, y, width, height in px.

## Shared on every page

| Element | Position | Content |
|---|---|---|
| Title block (text box) | 8, 6, 470, 60 | Page title in Segoe UI Semibold 20 pt, subtitle in 10 pt muted |
| 5 dropdown slicers | from x 488, y 12, each 106 × 50 | Date[Year] (single select), Date[Month] (single select), Region[Region], Channel[Channel], Product[Category] |
| Close period pill (card) | 1060, 12, 204, 50 | [Reporting Period Label] in white on navy `#0F1B2D` |
| Footer (card) | 1000, 700, 270, 20 | [Data As Of Label] |
| KPI tiles | y 76, height 106, equal widths across 1248 px with 12 px gaps | A card showing the value with the KPI title, plus a borderless card overlaid at the bottom showing the subtitle measure, coloured by a `Color …` measure |

Colour roles: **Actual** blue `#2A78D6` (solid, 3 px), **Forecast** orange `#EB6834` (dashed), **Budget** aqua `#1BAF7A` (dotted), **Prior year** grey `#A9A7A0`. Favourable/unfavourable use green `#0CA30C`/`#006300` and red `#D03B3B`, always paired with ▲/▼ or a sign, so colour is never the only cue.

## Executive Summary

One-screen answer to *how did we close the month?* Five headline KPIs with variance subtitles, the actual vs forecast vs budget trend, the YTD budget bridge, and category, region and channel breakdowns.

| # | Visual | Type | Position | Fields | Notes |
|---|---|---|---|---|---|
| 1 | Net Sales · Month | `card` | 16, 76, 240, 106 | **Values:** [Net Sales (Month)] |  |
| 2 | KPI subtitle | `card` | 22, 148, 228, 30 | **Values:** [KPI Label Net Sales (Month)] | Conditional colour from [Color Var % vs Forecast (Month)] |
| 3 | Gross Margin % · Month | `card` | 268, 76, 240, 106 | **Values:** [Gross Margin % (Month)] |  |
| 4 | KPI subtitle | `card` | 274, 148, 228, 30 | **Values:** [KPI Label Gross Margin % (Month)] | Conditional colour from [Color GM pts vs Budget (Month)] |
| 5 | Net Sales · YTD | `card` | 520, 76, 240, 106 | **Values:** [Net Sales (YTD)] |  |
| 6 | KPI subtitle | `card` | 526, 148, 228, 30 | **Values:** [KPI Label Net Sales (YTD)] | Conditional colour from [Color YoY % (YTD)] |
| 7 | Full-Year Outlook | `card` | 772, 76, 240, 106 | **Values:** [Full Year Outlook] |  |
| 8 | KPI subtitle | `card` | 778, 148, 228, 30 | **Values:** [KPI Label Outlook] | Conditional colour from [Color Outlook vs Budget] |
| 9 | Forecast Accuracy · Month | `card` | 1024, 76, 240, 106 | **Values:** [Forecast Accuracy % (Month)] |  |
| 10 | KPI subtitle | `card` | 1030, 148, 228, 30 | **Values:** [KPI Label Accuracy (Month)] | Conditional colour from [Color Accuracy vs Target (Month)] |
| 11 | Net sales: actual vs forecast vs budget | `lineChart` | 16, 194, 820, 262 | **Category:** Date[Month Year]<br>**Y:** [Net Sales], [Forecast Net Sales], [Budget Net Sales] | Visual filter: Month Offset −12 … +2<br>Sorted by Month Year (ascending) |
| 12 | YTD bridge: budget → actual | `waterfallChart` | 848, 194, 416, 262 | **Category:** Variance Bridge[Step]<br>**Y:** [Bridge Value (YTD)] as “Net sales” | Sorted by Step (ascending) |
| 13 | Net sales YTD by category | `clusteredBarChart` | 16, 468, 404, 228 | **Category:** Product[Category]<br>**Y:** [Net Sales (YTD)] as “Net sales YTD” | Sorted by Net Sales (YTD) (descending) |
| 14 | Regional scorecard | `pivotTable` | 432, 468, 500, 228 | **Rows:** Region[Region]<br>**Values:** [Net Sales (Month)] as “Month”, [Var % vs Forecast (Month)] as “vs Fcst”, [YoY % (Month)] as “YoY”, [Net Sales (YTD)] as “YTD”, [Var % vs Budget (YTD)] as “YTD vs Bud”, [Gross Margin % (YTD)] as “GM % YTD” | Conditional colour from [Color Var % vs Budget (YTD)], [Color Var % vs Forecast (Month)], [Color YoY % (Month)]<br>Sorted by Net Sales (YTD) (descending) |
| 15 | Channel mix · YTD | `clusteredBarChart` | 944, 468, 320, 228 | **Category:** Channel[Channel]<br>**Y:** [Channel Share (YTD)] as “Share of net sales YTD” | Sorted by Channel Share (YTD) (descending) |

## Variance Analysis

Explains *where and why* actuals differ from plan: monthly variance bars, forecast accuracy trend against target, and a category › brand › SKU variance matrix with region and channel splits.

| # | Visual | Type | Position | Fields | Notes |
|---|---|---|---|---|---|
| 1 | Variance vs Forecast · Month | `card` | 16, 76, 303, 106 | **Values:** [Var vs Forecast (Month)] |  |
| 2 | KPI subtitle | `card` | 22, 148, 291, 30 | **Values:** [KPI Label Var vs Forecast (Month)] | Conditional colour from [Color Var % vs Forecast (Month)] |
| 3 | Variance vs Budget · YTD | `card` | 331, 76, 303, 106 | **Values:** [Var vs Budget (YTD)] |  |
| 4 | KPI subtitle | `card` | 337, 148, 291, 30 | **Values:** [KPI Label Var vs Budget (YTD)] | Conditional colour from [Color Var % vs Budget (YTD)] |
| 5 | Forecast Accuracy · YTD | `card` | 646, 76, 303, 106 | **Values:** [Forecast Accuracy % (YTD)] |  |
| 6 | KPI subtitle | `card` | 652, 148, 291, 30 | **Values:** [KPI Label Accuracy (YTD)] | Conditional colour from [Color Accuracy vs Target (YTD)] |
| 7 | Forecast Bias · YTD | `card` | 961, 76, 303, 106 | **Values:** [Forecast Bias % (YTD)] |  |
| 8 | KPI subtitle | `card` | 967, 148, 291, 30 | **Values:** [KPI Label Bias (YTD)] | Conditional colour from [Color Bias (YTD)] |
| 9 | Monthly variance vs forecast | `clusteredColumnChart` | 16, 194, 620, 250 | **Category:** Date[Month Year]<br>**Y:** [Var vs Forecast] as “Variance vs forecast” | Visual filter: Month Offset −12 … 0<br>Conditional colour from [Fill Var vs Forecast]<br>Sorted by Month Year (ascending) |
| 10 | Forecast accuracy trend | `lineChart` | 648, 194, 616, 250 | **Category:** Date[Month Year]<br>**Y:** [Forecast Accuracy %] as “Accuracy (1 - WMAPE)”, [Forecast Accuracy Target] as “Target” | Visual filter: Month Offset −12 … 0<br>Sorted by Month Year (ascending) |
| 11 | Reporting month variance by category › brand › SKU | `pivotTable` | 16, 456, 820, 240 | **Rows:** Product[Category], Product[Brand], Product[Product]<br>**Values:** [Net Sales (Month)] as “Actual”, [Forecast Net Sales (Closed) (Month)] as “Forecast”, [Var vs Forecast (Month)] as “Var”, [Var % vs Forecast (Month)] as “Var %”, [Budget Net Sales (Closed) (Month)] as “Budget”, [Var vs Budget (Month)] as “Var vs Bud”, [Var % vs Budget (Month)] as “Var % Bud” | Conditional colour from [Color Var % vs Budget (Month)], [Color Var % vs Forecast (Month)]<br>Sorted by Net Sales (Month) (descending) |
| 12 | Month variance vs forecast by region | `clusteredBarChart` | 848, 456, 416, 116 | **Category:** Region[Region]<br>**Y:** [Var vs Forecast (Month)] as “Variance vs forecast” | Conditional colour from [Fill Var vs Forecast (Month)]<br>Sorted by Var vs Forecast (Month) (descending) |
| 13 | Month variance vs forecast by channel | `clusteredBarChart` | 848, 580, 416, 116 | **Category:** Channel[Channel]<br>**Y:** [Var vs Forecast (Month)] as “Variance vs forecast” | Conditional colour from [Fill Var vs Forecast (Month)]<br>Sorted by Var vs Forecast (Month) (descending) |

## Monthly & Quarterly KPIs

Time-intelligence view: QTD, YTD and rolling-12-month KPIs, the cumulative YTD race against budget, forecast and prior year, quarterly YoY comparison, and a Year › Quarter › Month KPI table.

| # | Visual | Type | Position | Fields | Notes |
|---|---|---|---|---|---|
| 1 | Net Sales · QTD | `card` | 16, 76, 240, 106 | **Values:** [Net Sales (QTD)] |  |
| 2 | KPI subtitle | `card` | 22, 148, 228, 30 | **Values:** [KPI Label QTD] | Conditional colour from [Color QoQ %] |
| 3 | Net Sales · YTD | `card` | 268, 76, 240, 106 | **Values:** [Net Sales (YTD)] |  |
| 4 | KPI subtitle | `card` | 274, 148, 228, 30 | **Values:** [KPI Label YTD YoY] | Conditional colour from [Color YoY % (YTD)] |
| 5 | Net Sales · Rolling 12M | `card` | 520, 76, 240, 106 | **Values:** [Net Sales (R12M)] |  |
| 6 | KPI subtitle | `card` | 526, 148, 228, 30 | **Values:** [KPI Label R12M] | Conditional colour from [Color YoY % (R12M)] |
| 7 | Gross Margin % · YTD | `card` | 772, 76, 240, 106 | **Values:** [Gross Margin % (YTD)] |  |
| 8 | KPI subtitle | `card` | 778, 148, 228, 30 | **Values:** [KPI Label GM % (YTD)] | Conditional colour from [Color GM pts vs PY (YTD)] |
| 9 | Discount % · YTD | `card` | 1024, 76, 240, 106 | **Values:** [Discount % (YTD)] |  |
| 10 | KPI subtitle | `card` | 1030, 148, 228, 30 | **Values:** [KPI Label Discount % (YTD)] | Conditional colour from [Color Discount pts vs PY (YTD)] |
| 11 | Cumulative net sales: current year | `lineChart` | 16, 194, 620, 250 | **Category:** Date[Month]<br>**Y:** [Net Sales Running YTD] as “Actual YTD”, [Budget Running YTD] as “Budget YTD”, [Forecast Running YTD] as “Forecast YTD”, [Net Sales Running YTD PY] as “Prior year YTD” | Visual filter: Year Offset = 0<br>Sorted by Month (ascending) |
| 12 | Quarterly net sales by year | `clusteredColumnChart` | 648, 194, 616, 250 | **Category:** Date[Quarter]<br>**Series:** Date[Year]<br>**Y:** [Net Sales] as “Net sales” | Sorted by Quarter (ascending) |
| 13 | Period KPI table | `pivotTable` | 16, 456, 820, 240 | **Rows:** Date[Year], Date[Quarter], Date[Month]<br>**Values:** [Net Sales] as “Net sales”, [PoP %] as “PoP %”, [YoY %] as “YoY %”, [Gross Margin %] as “GM %”, [Discount %] as “Disc %”, [Units Sold] as “Units”, [Avg Net Price] as “Net price”, [Var % vs Budget] as “vs Budget”, [Forecast Accuracy %] as “Fcst acc.” | Conditional colour from [Color PoP %], [Color Var % vs Budget], [Color YoY %]<br>Sorted by Year (descending) |
| 14 | Gross margin % vs budget | `lineChart` | 848, 456, 416, 240 | **Category:** Date[Month Year]<br>**Y:** [Gross Margin %] as “Actual GM %”, [Budget Gross Margin %] as “Budget GM %” | Visual filter: Month Offset −12 … 0<br>Sorted by Month Year (ascending) |

## Product & Region Drilldown

Drilldown for commercial teams: portfolio matrix with drill, SKU growth vs margin scatter, region vs prior year, a region × channel-group grid and a customer ranking.

| # | Visual | Type | Position | Fields | Notes |
|---|---|---|---|---|---|
| 1 | Portfolio performance | `pivotTable` | 16, 76, 720, 330 | **Rows:** Product[Category], Product[Brand], Product[Product]<br>**Values:** [Net Sales (YTD)] as “Net sales YTD”, [Share of Net Sales (YTD)] as “Share”, [YoY % (YTD)] as “YoY”, [Gross Margin % (YTD)] as “GM %”, [Var % vs Forecast (YTD)] as “vs Fcst”, [Var % vs Budget (YTD)] as “vs Bud”, [Units Sold (YTD)] as “Units” | Conditional colour from [Color Var % vs Budget (YTD)], [Color Var % vs Forecast (YTD)], [Color YoY % (YTD)]<br>Sorted by Net Sales (YTD) (descending) |
| 2 | SKU portfolio: growth vs margin | `scatterChart` | 748, 76, 516, 330 | **Category:** Product[Product]<br>**X:** [YoY % (YTD)] as “YoY growth”<br>**Y:** [Gross Margin % (YTD)] as “Gross margin %”<br>**Size:** [Net Sales (YTD)] as “Net sales YTD” |  |
| 3 | Region: YTD vs prior year | `clusteredBarChart` | 16, 418, 400, 278 | **Category:** Region[Region]<br>**Y:** [Net Sales (YTD)] as “Net sales YTD”, [Net Sales (PY YTD)] as “Prior year YTD” | Sorted by Net Sales (YTD) (descending) |
| 4 | Region × channel group · YTD | `pivotTable` | 428, 418, 420, 278 | **Rows:** Region[Region]<br>**Columns:** Channel[Channel Group]<br>**Values:** [Net Sales (YTD)] as “Net sales YTD” |  |
| 5 | Customer ranking · YTD | `tableEx` | 860, 418, 404, 278 | **Values:** [Customer Rank (YTD)] as “#”, Customer[Customer], [Net Sales (YTD)] as “Net sales YTD”, [YoY % (YTD)] as “YoY”, [Gross Margin % (YTD)] as “GM %” | Conditional colour from [Color YoY % (YTD)]<br>Sorted by Net Sales (YTD) (descending) |

## Interaction notes

* All visuals cross-filter each other (default interactions). Slicers sync by field name across pages if you enable *View › Sync slicers*.
* Matrices are built with Category › Brand › Product (or Year › Quarter › Month) on Rows. Use the drill buttons or *Expand all* to go deeper.
* Choosing a Year without a Month moves the anchor to that year's last closed month. Choosing a Month too shows that exact close.
* Trend visuals use the `Month Offset` window filters, so they always show the latest 13 closed months without manual date maintenance.
