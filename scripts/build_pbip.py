"""
Builds the Power BI Project (PBIP) for the FMCG Month-End Financial Reporting dashboard:

  pbip/FMCG_MonthEnd.pbip
  pbip/FMCG_MonthEnd.SemanticModel/   (TMDL: star schema, Power Query M, DAX measures)
  pbip/FMCG_MonthEnd.Report/          (PBIR: 4 report pages, custom theme)

and the companion artefacts that are generated from the same definitions:
  powerquery/*.pq, dax/measures.dax, theme/Aurora_FMCG_Theme.json, docs/dax-measure-library.md

Everything is defined once in this file so the model, the docs and the DAX script never drift apart.
Run:  python build_pbip.py
"""
import json
import os
import shutil
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NAME = "FMCG_MonthEnd"
PBIP = os.path.join(ROOT, "pbip")
SM = os.path.join(PBIP, f"{NAME}.SemanticModel")
RP = os.path.join(PBIP, f"{NAME}.Report")
NS = uuid.UUID("6f1c8a52-3b0e-4f3e-9a51-0c2b7d1e4a90")


def tag(*parts):
    return str(uuid.uuid5(NS, "/".join(parts)))


def q(name):
    """Quote a TMDL object name when needed."""
    safe = name.replace("_", "").isalnum() and not name[0].isdigit() and name not in ("Date",)
    return name if safe else "'" + name.replace("'", "''") + "'"


# ======================================================================================
# Palette (validated categorical slots + status colours; see docs)
# ======================================================================================
PAL = {
    "blue": "#2A78D6", "orange": "#EB6834", "aqua": "#1BAF7A", "yellow": "#EDA100",
    "magenta": "#E87BA4", "green": "#008300", "violet": "#6250D6", "red": "#E34948",
    "ink": "#0B0B0B", "ink2": "#52514E", "muted": "#898781", "grid": "#E1E0D9", "axis": "#C3C2B7",
    "surface": "#FFFFFF", "page": "#F4F3EF", "good": "#0CA30C", "goodText": "#006300", "bad": "#D03B3B",
    "warn": "#FAB219", "navy": "#0F1B2D",
}
ACTUAL, FORECAST, BUDGET, PRIOR = PAL["blue"], PAL["orange"], PAL["aqua"], "#A9A7A0"

# ======================================================================================
# Power Query (M)
# ======================================================================================
DATA_FOLDER_DEFAULT = r"C:\FMCG-MonthEnd\data\\"[:-1]


def csv_source(file, ncols):
    return (f'Source = Csv.Document(File.Contents(DataFolder & "{file}"), '
            f'[Delimiter = ",", Columns = {ncols}, Encoding = 65001, QuoteStyle = QuoteStyle.Csv])')


M = {}
M["Date"] = """let
    // Calendar covering every actual, forecast and budget period
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    AsTable = Table.FromList(Dates, Splitter.SplitByNothing(), type table [Date = date]),
    AddYear = Table.AddColumn(AsTable, "Year", each Date.Year([Date]), Int64.Type),
    AddQuarterNo = Table.AddColumn(AddYear, "Quarter No", each Date.QuarterOfYear([Date]), Int64.Type),
    AddQuarter = Table.AddColumn(AddQuarterNo, "Quarter", each "Q" & Text.From([Quarter No]), type text),
    AddYearQuarter = Table.AddColumn(AddQuarter, "Year Quarter", each Text.From([Year]) & " Q" & Text.From([Quarter No]), type text),
    AddYearQuarterKey = Table.AddColumn(AddYearQuarter, "Year Quarter Key", each [Year] * 10 + [Quarter No], Int64.Type),
    AddMonthNo = Table.AddColumn(AddYearQuarterKey, "Month No", each Date.Month([Date]), Int64.Type),
    AddMonth = Table.AddColumn(AddMonthNo, "Month", each Date.ToText([Date], "MMM", "en-US"), type text),
    AddMonthName = Table.AddColumn(AddMonth, "Month Name", each Date.ToText([Date], "MMMM", "en-US"), type text),
    AddMonthYear = Table.AddColumn(AddMonthName, "Month Year", each Date.ToText([Date], "MMM yyyy", "en-US"), type text),
    AddYearMonthKey = Table.AddColumn(AddMonthYear, "Year Month Key", each [Year] * 100 + [Month No], Int64.Type),
    AddMonthStart = Table.AddColumn(AddYearMonthKey, "Month Start", each Date.StartOfMonth([Date]), type date),
    AddMonthEnd = Table.AddColumn(AddMonthStart, "Month End", each Date.EndOfMonth([Date]), type date),
    AddHalf = Table.AddColumn(AddMonthEnd, "Half", each if [Month No] <= 6 then "H1" else "H2", type text),
    AddDay = Table.AddColumn(AddHalf, "Day", each Date.Day([Date]), Int64.Type),
    AddWeekdayNo = Table.AddColumn(AddDay, "Weekday No", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddWeekday = Table.AddColumn(AddWeekdayNo, "Weekday", each Date.ToText([Date], "ddd", "en-US"), type text),
    AddWeekOfYear = Table.AddColumn(AddWeekday, "Week of Year", each Date.WeekOfYear([Date], Day.Monday), Int64.Type),
    AddIsWeekend = Table.AddColumn(AddWeekOfYear, "Is Weekend", each [Weekday No] >= 6, type logical)
in
    AddIsWeekend"""

M["Product"] = f"""let
    {csv_source("dim_product.csv", 10)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"ProductKey", Int64.Type}}, {{"SKU", type text}}, {{"ProductName", type text}}, {{"Brand", type text}},
        {{"Category", type text}}, {{"Segment", type text}}, {{"PackType", type text}},
        {{"UnitListPrice", type number}}, {{"UnitCost", type number}}, {{"LaunchDate", type date}}}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {{
        {{"ProductName", "Product"}}, {{"PackType", "Pack Type"}}, {{"UnitListPrice", "List Price"}},
        {{"UnitCost", "Standard Cost"}}, {{"LaunchDate", "Launch Date"}}}}),
    AddPriceBand = Table.AddColumn(Renamed, "Price Band", each
        if [List Price] < 2 then "Under $2"
        else if [List Price] < 5 then "$2 - $5"
        else if [List Price] < 10 then "$5 - $10"
        else "$10+", type text),
    AddStdMargin = Table.AddColumn(AddPriceBand, "Standard Margin %", each 1 - [Standard Cost] / [List Price], Percentage.Type)
in
    AddStdMargin"""

M["Customer"] = f"""let
    {csv_source("dim_customer.csv", 8)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"CustomerKey", Int64.Type}}, {{"CustomerCode", type text}}, {{"CustomerName", type text}}, {{"City", type text}},
        {{"RegionKey", Int64.Type}}, {{"ChannelKey", Int64.Type}}, {{"CustomerTier", type text}}, {{"CustomerSince", type date}}}}, "en-US"),
    // Region and channel are conformed dimensions joined to the facts directly (no snowflake)
    RemovedKeys = Table.RemoveColumns(ChangedType, {{"RegionKey", "ChannelKey"}}),
    Renamed = Table.RenameColumns(RemovedKeys, {{
        {{"CustomerCode", "Customer Code"}}, {{"CustomerName", "Customer"}}, {{"CustomerTier", "Customer Tier"}}, {{"CustomerSince", "Customer Since"}}}}),
    AddTierOrder = Table.AddColumn(Renamed, "Tier Order", each
        if [Customer Tier] = "Key Account" then 1 else if [Customer Tier] = "Gold" then 2
        else if [Customer Tier] = "Silver" then 3 else 4, Int64.Type)
in
    AddTierOrder"""

M["Region"] = f"""let
    {csv_source("dim_region.csv", 3)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"RegionKey", Int64.Type}}, {{"Region", type text}}, {{"RegionalDirector", type text}}}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {{{{"RegionalDirector", "Regional Director"}}}})
in
    Renamed"""

M["Channel"] = f"""let
    {csv_source("dim_channel.csv", 3)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"ChannelKey", Int64.Type}}, {{"Channel", type text}}, {{"ChannelGroup", type text}}}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {{{{"ChannelGroup", "Channel Group"}}}})
in
    Renamed"""

M["Fact Sales"] = f"""let
    {csv_source("fact_sales.csv", 14)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"SalesLineID", Int64.Type}}, {{"OrderNumber", type text}}, {{"OrderDate", type date}},
        {{"ProductKey", Int64.Type}}, {{"CustomerKey", Int64.Type}}, {{"RegionKey", Int64.Type}}, {{"ChannelKey", Int64.Type}},
        {{"Units", Int64.Type}}, {{"UnitListPrice", type number}}, {{"GrossSales", type number}},
        {{"DiscountAmount", type number}}, {{"NetSales", type number}}, {{"COGS", type number}}}}, "en-US"),
    // Guard rails: drop malformed rows rather than failing the whole refresh
    RemovedErrors = Table.RemoveRowsWithErrors(ChangedType, {{"OrderDate", "ProductKey", "NetSales"}}),
    FilteredValid = Table.SelectRows(RemovedErrors, each [OrderDate] <> null and [Units] <> null)
in
    FilteredValid"""

M["Fact Forecast"] = f"""let
    {csv_source("fact_forecast.csv", 13)},
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{
        {{"ForecastLineID", Int64.Type}}, {{"MonthStartDate", type date}}, {{"ForecastVersion", type text}},
        {{"ProductKey", Int64.Type}}, {{"RegionKey", Int64.Type}}, {{"ChannelKey", Int64.Type}},
        {{"ForecastUnits", Int64.Type}}, {{"ForecastNetSales", type number}}, {{"ForecastCOGS", type number}},
        {{"BudgetUnits", Int64.Type}}, {{"BudgetNetSales", type number}}, {{"BudgetCOGS", type number}}}}, "en-US"),
    RemovedErrors = Table.RemoveRowsWithErrors(ChangedType, {{"MonthStartDate", "ProductKey"}})
in
    RemovedErrors"""

M["Variance Bridge"] = """let
    // Disconnected helper table that drives the Budget -> Actual waterfall
    Source = #table(
        type table [Step = text, #"Step Order" = Int64.Type],
        {{"Budget", 1}, {"Volume & Mix", 2}, {"Price & Discount", 3}})
in
    Source"""

M["_Measures"] = """let
    Source = #table(type table [MeasureHelper = text], {})
in
    Source"""

# ======================================================================================
# Tables & columns
#   (name, dataType, flags)  flags: hidden, key, fmt, sortBy, sum, cat(dataCategory)
# ======================================================================================
TABLES = {
    "Date": {
        "group": "Dimensions", "dataCategory": "Time",
        "columns": [
            ("Date", "dateTime", dict(key=True, fmt="dd mmm yyyy")),
            ("Year", "int64", dict(fmt="0")),
            ("Quarter No", "int64", dict(hidden=True, fmt="0")),
            ("Quarter", "string", dict(sortBy="Quarter No")),
            ("Year Quarter", "string", dict(sortBy="Year Quarter Key")),
            ("Year Quarter Key", "int64", dict(hidden=True, fmt="0")),
            ("Month No", "int64", dict(hidden=True, fmt="0")),
            ("Month", "string", dict(sortBy="Month No")),
            ("Month Name", "string", dict(sortBy="Month No")),
            ("Month Year", "string", dict(sortBy="Year Month Key")),
            ("Year Month Key", "int64", dict(hidden=True, fmt="0")),
            ("Month Start", "dateTime", dict(fmt="mmm yyyy")),
            ("Month End", "dateTime", dict(fmt="dd mmm yyyy")),
            ("Half", "string", {}),
            ("Day", "int64", dict(fmt="0")),
            ("Weekday No", "int64", dict(hidden=True, fmt="0")),
            ("Weekday", "string", dict(sortBy="Weekday No")),
            ("Week of Year", "int64", dict(fmt="0")),
            ("Is Weekend", "boolean", {}),
        ],
        "calculated": [
            ("Is Actual Period", "boolean",
             "'Date'[Date] <= EOMONTH ( MAX ( 'Fact Sales'[OrderDate] ), 0 )",
             "TRUE for every date up to the end of the latest month that has actuals (the last closed month)."),
            ("Month Offset", "int64",
             "VAR _last = EOMONTH ( MAX ( 'Fact Sales'[OrderDate] ), 0 )\nRETURN\n    ( 'Date'[Year] * 12 + 'Date'[Month No] ) - ( YEAR ( _last ) * 12 + MONTH ( _last ) )",
             "0 = last closed month, -1 = the month before, +1 = first forecast-only month. Drives the rolling-window visual filters."),
            ("Year Offset", "int64",
             "'Date'[Year] - YEAR ( MAX ( 'Fact Sales'[OrderDate] ) )",
             "0 = the year of the last closed month, -1 = prior year."),
        ],
        "hierarchies": [("Calendar", ["Year", "Quarter", "Month", "Date"])],
    },
    "Product": {
        "group": "Dimensions",
        "columns": [
            ("ProductKey", "int64", dict(hidden=True, fmt="0")),
            ("SKU", "string", {}), ("Product", "string", {}), ("Brand", "string", {}), ("Category", "string", {}),
            ("Segment", "string", {}), ("Pack Type", "string", {}),
            ("List Price", "double", dict(fmt="\\$#,0.00")), ("Standard Cost", "double", dict(fmt="\\$#,0.00")),
            ("Launch Date", "dateTime", dict(fmt="dd mmm yyyy")), ("Price Band", "string", {}),
            ("Standard Margin %", "double", dict(fmt="0.0%")),
        ],
        "hierarchies": [("Product Hierarchy", ["Category", "Brand", "Product"])],
    },
    "Customer": {
        "group": "Dimensions",
        "columns": [
            ("CustomerKey", "int64", dict(hidden=True, fmt="0")),
            ("Customer Code", "string", {}), ("Customer", "string", {}), ("City", "string", {}),
            ("Customer Tier", "string", dict(sortBy="Tier Order")), ("Customer Since", "dateTime", dict(fmt="dd mmm yyyy")),
            ("Tier Order", "int64", dict(hidden=True, fmt="0")),
        ],
    },
    "Region": {
        "group": "Dimensions",
        "columns": [("RegionKey", "int64", dict(hidden=True, fmt="0")), ("Region", "string", {}), ("Regional Director", "string", {})],
    },
    "Channel": {
        "group": "Dimensions",
        "columns": [("ChannelKey", "int64", dict(hidden=True, fmt="0")), ("Channel", "string", {}), ("Channel Group", "string", {})],
    },
    "Fact Sales": {
        "group": "Facts",
        "columns": [
            ("SalesLineID", "int64", dict(hidden=True, fmt="0")), ("OrderNumber", "string", dict(hidden=True)),
            ("OrderDate", "dateTime", dict(hidden=True, fmt="dd mmm yyyy")),
            ("ProductKey", "int64", dict(hidden=True, fmt="0")), ("CustomerKey", "int64", dict(hidden=True, fmt="0")),
            ("RegionKey", "int64", dict(hidden=True, fmt="0")), ("ChannelKey", "int64", dict(hidden=True, fmt="0")),
            ("Units", "int64", dict(hidden=True, fmt="#,0", sum=True)), ("UnitListPrice", "double", dict(hidden=True, fmt="\\$#,0.00")),
            ("GrossSales", "double", dict(hidden=True, fmt="\\$#,0", sum=True)), ("DiscountAmount", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
            ("NetSales", "double", dict(hidden=True, fmt="\\$#,0", sum=True)), ("COGS", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
        ],
    },
    "Fact Forecast": {
        "group": "Facts",
        "columns": [
            ("ForecastLineID", "int64", dict(hidden=True, fmt="0")), ("MonthStartDate", "dateTime", dict(hidden=True, fmt="mmm yyyy")),
            ("ForecastVersion", "string", dict(hidden=True)),
            ("ProductKey", "int64", dict(hidden=True, fmt="0")), ("RegionKey", "int64", dict(hidden=True, fmt="0")),
            ("ChannelKey", "int64", dict(hidden=True, fmt="0")),
            ("ForecastUnits", "int64", dict(hidden=True, fmt="#,0", sum=True)), ("ForecastNetSales", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
            ("ForecastCOGS", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
            ("BudgetUnits", "int64", dict(hidden=True, fmt="#,0", sum=True)), ("BudgetNetSales", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
            ("BudgetCOGS", "double", dict(hidden=True, fmt="\\$#,0", sum=True)),
        ],
    },
    "Variance Bridge": {
        "group": "Helpers",
        "columns": [("Step", "string", dict(sortBy="Step Order")), ("Step Order", "int64", dict(hidden=True, fmt="0"))],
    },
    "_Measures": {
        "group": "Helpers",
        "columns": [("MeasureHelper", "string", dict(hidden=True))],
    },
}

RELATIONSHIPS = [
    ("Fact Sales", "OrderDate", "Date", "Date"),
    ("Fact Sales", "ProductKey", "Product", "ProductKey"),
    ("Fact Sales", "CustomerKey", "Customer", "CustomerKey"),
    ("Fact Sales", "RegionKey", "Region", "RegionKey"),
    ("Fact Sales", "ChannelKey", "Channel", "ChannelKey"),
    ("Fact Forecast", "MonthStartDate", "Date", "Date"),
    ("Fact Forecast", "ProductKey", "Product", "ProductKey"),
    ("Fact Forecast", "RegionKey", "Region", "RegionKey"),
    ("Fact Forecast", "ChannelKey", "Channel", "ChannelKey"),
]

# ======================================================================================
# DAX measure library
# ======================================================================================
CUR = "\\$#,0;(\\$#,0);\\$#,0"
CUR_VAR = "+\\$#,0;-\\$#,0;\\$#,0"
PCT = "0.0%;-0.0%;0.0%"
PCT_VAR = "+0.0%;-0.0%;0.0%"
INT = "#,0"

MEASURES = []  # (name, expression, format, folder, description)


def add(name, expr, fmt, folder, desc):
    MEASURES.append((name, expr.strip("\n"), fmt, folder, desc))


F_BASE, F_PLAN, F_VAR, F_ACC, F_PER, F_TI, F_OUT, F_RANK, F_UI = (
    "01 Actuals", "02 Forecast & Budget", "03 Variance", "04 Forecast Accuracy",
    "05 Reporting Period", "06 Time Intelligence (context)", "07 Outlook & KPIs", "08 Ranking & Mix", "09 Labels & Formatting")

# ---- 01 Actuals --------------------------------------------------------------------------
add("Gross Sales", "SUM ( 'Fact Sales'[GrossSales] )", CUR, F_BASE, "Invoice value at list price, before trade discounts.")
add("Discounts", "SUM ( 'Fact Sales'[DiscountAmount] )", CUR, F_BASE, "Trade and promotional discounts.")
add("Net Sales", "SUM ( 'Fact Sales'[NetSales] )", CUR, F_BASE, "Gross sales less discounts. The headline revenue measure.")
add("COGS", "SUM ( 'Fact Sales'[COGS] )", CUR, F_BASE, "Cost of goods sold at standard cost.")
add("Gross Margin", "[Net Sales] - [COGS]", CUR, F_BASE, "Net sales less COGS.")
add("Gross Margin %", "DIVIDE ( [Gross Margin], [Net Sales] )", PCT, F_BASE, "Gross margin as a share of net sales.")
add("Units Sold", "SUM ( 'Fact Sales'[Units] )", INT, F_BASE, "Units invoiced.")
add("Discount %", "DIVIDE ( [Discounts], [Gross Sales] )", PCT, F_BASE, "Discounts as a share of gross sales.")
add("Avg Net Price", "DIVIDE ( [Net Sales], [Units Sold] )", "\\$#,0.00", F_BASE, "Net sales per unit.")
add("Orders", "DISTINCTCOUNT ( 'Fact Sales'[OrderNumber] )", INT, F_BASE, "Number of distinct sales orders.")
add("Avg Order Value", "DIVIDE ( [Net Sales], [Orders] )", "\\$#,0", F_BASE, "Net sales per order.")
add("Active Customers", "DISTINCTCOUNT ( 'Fact Sales'[CustomerKey] )", INT, F_BASE, "Customers with at least one invoice in context.")
add("Active SKUs", "DISTINCTCOUNT ( 'Fact Sales'[ProductKey] )", INT, F_BASE, "SKUs with at least one invoice in context.")

# ---- 02 Forecast & Budget -----------------------------------------------------------------
add("Forecast Net Sales", "SUM ( 'Fact Forecast'[ForecastNetSales] )", CUR, F_PLAN, "Latest rolling forecast of net sales (all periods, including future months).")
add("Forecast Units", "SUM ( 'Fact Forecast'[ForecastUnits] )", INT, F_PLAN, "Latest rolling forecast of units.")
add("Forecast COGS", "SUM ( 'Fact Forecast'[ForecastCOGS] )", CUR, F_PLAN, "Forecast cost of goods sold.")
add("Forecast Gross Margin", "[Forecast Net Sales] - [Forecast COGS]", CUR, F_PLAN, "Forecast net sales less forecast COGS.")
add("Forecast Gross Margin %", "DIVIDE ( [Forecast Gross Margin], [Forecast Net Sales] )", PCT, F_PLAN, "Forecast gross margin %.")
add("Budget Net Sales", "SUM ( 'Fact Forecast'[BudgetNetSales] )", CUR, F_PLAN, "Annual operating plan (budget) net sales.")
add("Budget Units", "SUM ( 'Fact Forecast'[BudgetUnits] )", INT, F_PLAN, "Budget units.")
add("Budget COGS", "SUM ( 'Fact Forecast'[BudgetCOGS] )", CUR, F_PLAN, "Budget cost of goods sold.")
add("Budget Gross Margin", "[Budget Net Sales] - [Budget COGS]", CUR, F_PLAN, "Budget net sales less budget COGS.")
add("Budget Gross Margin %", "DIVIDE ( [Budget Gross Margin], [Budget Net Sales] )", PCT, F_PLAN, "Budget gross margin %.")
for nm, base in [("Forecast Net Sales (Closed)", "Forecast Net Sales"), ("Forecast Units (Closed)", "Forecast Units"),
                 ("Forecast Gross Margin (Closed)", "Forecast Gross Margin"), ("Budget Net Sales (Closed)", "Budget Net Sales"),
                 ("Budget Units (Closed)", "Budget Units"), ("Budget Gross Margin (Closed)", "Budget Gross Margin")]:
    add(nm, f"CALCULATE ( [{base}], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )",
        INT if "Units" in nm else CUR, F_PLAN,
        f"{base} restricted to closed periods, so it is like-for-like with actuals (future months are excluded).")
add("Budget Gross Margin % (Closed)", "DIVIDE ( [Budget Gross Margin (Closed)], [Budget Net Sales (Closed)] )", PCT, F_PLAN, "Budget GM % for closed periods.")

# ---- 03 Variance ---------------------------------------------------------------------------
add("Var vs Forecast", """
VAR _act = [Net Sales]
VAR _fc = [Forecast Net Sales (Closed)]
RETURN
    IF ( NOT ISBLANK ( _act ) || NOT ISBLANK ( _fc ), _act - _fc )""", CUR_VAR, F_VAR, "Actual net sales minus forecast (closed periods). Positive = favourable.")
add("Var % vs Forecast", "DIVIDE ( [Var vs Forecast], [Forecast Net Sales (Closed)] )", PCT_VAR, F_VAR, "Variance to forecast as a % of forecast.")
add("Var vs Budget", """
VAR _act = [Net Sales]
VAR _bud = [Budget Net Sales (Closed)]
RETURN
    IF ( NOT ISBLANK ( _act ) || NOT ISBLANK ( _bud ), _act - _bud )""", CUR_VAR, F_VAR, "Actual net sales minus budget (closed periods). Positive = favourable.")
add("Var % vs Budget", "DIVIDE ( [Var vs Budget], [Budget Net Sales (Closed)] )", PCT_VAR, F_VAR, "Variance to budget as a % of budget.")
add("Units Var vs Forecast", "IF ( NOT ISBLANK ( [Units Sold] ), [Units Sold] - [Forecast Units (Closed)] )", "+#,0;-#,0;0", F_VAR, "Units sold minus forecast units.")
add("Units Var % vs Forecast", "DIVIDE ( [Units Var vs Forecast], [Forecast Units (Closed)] )", PCT_VAR, F_VAR, "Unit variance to forecast as a %.")
add("GM Var vs Budget", "IF ( NOT ISBLANK ( [Net Sales] ), [Gross Margin] - [Budget Gross Margin (Closed)] )", CUR_VAR, F_VAR, "Gross margin minus budget gross margin.")
add("GM % pts vs Budget", "IF ( NOT ISBLANK ( [Net Sales] ), [Gross Margin %] - [Budget Gross Margin % (Closed)] )", "+0.0%;-0.0%;0.0%", F_VAR, "Gross margin % minus budget GM % (percentage points).")
add("Volume & Mix Effect vs Budget", """
VAR _grid =
    ADDCOLUMNS (
        CROSSJOIN (
            CALCULATETABLE ( VALUES ( 'Date'[Year Month Key] ), 'Date'[Is Actual Period] = TRUE () ),
            VALUES ( 'Product'[ProductKey] )
        ),
        "@ua", [Units Sold],
        "@na", [Net Sales],
        "@ub", [Budget Units],
        "@nb", [Budget Net Sales]
    )
RETURN
    SUMX (
        _grid,
        IF ( [@ub] = 0, [@na] - [@nb], ( [@ua] - [@ub] ) * DIVIDE ( [@nb], [@ub] ) )
    )""", CUR_VAR, F_VAR, "Part of the budget variance explained by units (SKU x month grain): (actual units - budget units) x budget price. Includes SKU mix.")
add("Price & Discount Effect vs Budget", "[Var vs Budget] - [Volume & Mix Effect vs Budget]", CUR_VAR, F_VAR,
    "Part of the budget variance explained by realised net price (list price changes and discount depth). Volume + Price = total variance.")
add("Bridge Value", """
SWITCH (
    SELECTEDVALUE ( 'Variance Bridge'[Step] ),
    "Budget", [Budget Net Sales (Closed)],
    "Volume & Mix", [Volume & Mix Effect vs Budget],
    "Price & Discount", [Price & Discount Effect vs Budget]
)""", CUR, F_VAR, "Feeds the Budget -> Actual waterfall. The waterfall total equals actual net sales.")

# ---- 04 Forecast accuracy -----------------------------------------------------------------
add("Forecast Accuracy Target", "0.90", "0%", F_ACC, "Target forecast accuracy (1 - WMAPE).")
add("Forecast Abs Error", """
VAR _grid =
    CROSSJOIN (
        CALCULATETABLE ( VALUES ( 'Date'[Year Month Key] ), 'Date'[Is Actual Period] = TRUE () ),
        VALUES ( 'Product'[ProductKey] ),
        VALUES ( 'Region'[RegionKey] )
    )
RETURN
    SUMX ( _grid, ABS ( [Net Sales] - [Forecast Net Sales] ) )""", CUR, F_ACC,
    "Sum of absolute forecast errors at SKU x Region x Month grain (errors don't cancel out across SKUs).")
add("WMAPE %", "DIVIDE ( [Forecast Abs Error], [Net Sales] )", PCT, F_ACC, "Weighted mean absolute percentage error = sum |actual - forecast| / sum actual.")
add("Forecast Accuracy %", "IF ( NOT ISBLANK ( [Net Sales] ), MAX ( 0, 1 - [WMAPE %] ) )", PCT, F_ACC, "1 - WMAPE, floored at 0. The standard demand-planning accuracy KPI.")
add("MAPE %", """
VAR _grid =
    ADDCOLUMNS (
        CROSSJOIN (
            CALCULATETABLE ( VALUES ( 'Date'[Year Month Key] ), 'Date'[Is Actual Period] = TRUE () ),
            VALUES ( 'Product'[ProductKey] )
        ),
        "@a", [Net Sales],
        "@f", [Forecast Net Sales]
    )
RETURN
    AVERAGEX ( FILTER ( _grid, [@a] > 0 ), ABS ( [@a] - [@f] ) / [@a] )""", PCT, F_ACC, "Unweighted mean absolute percentage error across SKU x Month cells (every SKU counts equally).")
add("Forecast Bias %", "DIVIDE ( [Forecast Net Sales (Closed)] - [Net Sales], [Net Sales] )", PCT_VAR, F_ACC, "Positive = over-forecasting, negative = under-forecasting.")
add("Accuracy vs Target (pts)", "IF ( NOT ISBLANK ( [Forecast Accuracy %] ), [Forecast Accuracy %] - [Forecast Accuracy Target] )", "+0.0%;-0.0%;0.0%", F_ACC, "Forecast accuracy minus target, in percentage points.")

# ---- 05 Reporting period (anchored to the last closed month or the slicer selection) -------
add("Last Actual Date", "EOMONTH ( CALCULATE ( MAX ( 'Fact Sales'[OrderDate] ), REMOVEFILTERS () ), 0 )", "dd mmm yyyy", F_PER,
    "Month-end of the latest month with actuals, regardless of filters.")
add("Reporting Date", """
VAR _last = [Last Actual Date]
VAR _minCtx = MIN ( 'Date'[Date] )
VAR _maxCtx = MAX ( 'Date'[Date] )
RETURN
    IF ( _minCtx <= _last, MIN ( _maxCtx, _last ) )""", "dd mmm yyyy", F_PER,
    "The as-of date for every (Month)/(QTD)/(YTD) measure: the end of the selected period, capped at the last closed month. With no date selection it is the last closed month.")

PERIODS = {
    "Month": ("EOMONTH ( _rd, -1 ) + 1", "_rd"),
    "Prior Month": ("EOMONTH ( _rd, -2 ) + 1", "EOMONTH ( _rd, -1 )"),
    "PY Month": ("EOMONTH ( _rd, -13 ) + 1", "EOMONTH ( _rd, -12 )"),
    "QTD": ("DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 )", "_rd"),
    "Prior QTD": ("DATE ( YEAR ( EOMONTH ( _rd, -3 ) ), QUARTER ( EOMONTH ( _rd, -3 ) ) * 3 - 2, 1 )", "EOMONTH ( _rd, -3 )"),
    "PY QTD": ("DATE ( YEAR ( _rd ) - 1, QUARTER ( _rd ) * 3 - 2, 1 )", "EOMONTH ( _rd, -12 )"),
    "YTD": ("DATE ( YEAR ( _rd ), 1, 1 )", "_rd"),
    "PY YTD": ("DATE ( YEAR ( _rd ) - 1, 1, 1 )", "EOMONTH ( _rd, -12 )"),
    "R12M": ("EOMONTH ( _rd, -12 ) + 1", "_rd"),
    "PY R12M": ("EOMONTH ( _rd, -24 ) + 1", "EOMONTH ( _rd, -12 )"),
}
PERIOD_DESC = {
    "Month": "the reporting month", "Prior Month": "the month before the reporting month",
    "PY Month": "the same month last year", "QTD": "quarter-to-date through the reporting month",
    "Prior QTD": "the equivalent quarter-to-date one quarter earlier", "PY QTD": "the same quarter-to-date last year",
    "YTD": "year-to-date through the reporting month", "PY YTD": "the same year-to-date period last year",
    "R12M": "the rolling 12 months ending with the reporting month", "PY R12M": "the rolling 12 months one year earlier",
}


def period_measure(base, period, fmt, folder=F_PER):
    start, end = PERIODS[period]
    expr = f"""
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [{base}], DATESBETWEEN ( 'Date'[Date], {start}, {end} ) )
    )"""
    add(f"{base} ({period})", expr, fmt, folder, f"[{base}] for {PERIOD_DESC[period]}.")


for p in PERIODS:
    period_measure("Net Sales", p, CUR)
for p in ["Month", "PY Month", "QTD", "YTD", "PY YTD"]:
    period_measure("Gross Margin", p, CUR)
    period_measure("Gross Margin %", p, PCT)
for p in ["Month", "YTD", "PY YTD"]:
    period_measure("Units Sold", p, INT)
    period_measure("Discount %", p, PCT)
for p in ["Month", "QTD", "YTD"]:
    for b, f in [("Forecast Net Sales (Closed)", CUR), ("Budget Net Sales (Closed)", CUR), ("Var vs Forecast", CUR_VAR),
                 ("Var % vs Forecast", PCT_VAR), ("Var vs Budget", CUR_VAR), ("Var % vs Budget", PCT_VAR),
                 ("Forecast Accuracy %", PCT), ("Forecast Bias %", PCT_VAR), ("GM % pts vs Budget", "+0.0%;-0.0%;0.0%")]:
        period_measure(b, p, f)
period_measure("Bridge Value", "YTD", CUR)
period_measure("Bridge Value", "Month", CUR)
period_measure("Active Customers", "Month", INT)
period_measure("Active Customers", "YTD", INT)
period_measure("Avg Order Value", "YTD", "\\$#,0")


def growth(name, cur, prev, desc):
    add(name, f"""
VAR _cur = [{cur}]
VAR _prev = [{prev}]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )""", PCT_VAR, F_PER, desc)


growth("MoM %", "Net Sales (Month)", "Net Sales (Prior Month)", "Month-over-month growth of net sales for the reporting month.")
growth("YoY % (Month)", "Net Sales (Month)", "Net Sales (PY Month)", "Reporting month vs the same month last year.")
growth("QoQ %", "Net Sales (QTD)", "Net Sales (Prior QTD)", "Quarter-to-date vs the equivalent period of the prior quarter.")
growth("YoY % (QTD)", "Net Sales (QTD)", "Net Sales (PY QTD)", "Quarter-to-date vs the same period last year.")
growth("YoY % (YTD)", "Net Sales (YTD)", "Net Sales (PY YTD)", "Year-to-date vs the same period last year.")
growth("YoY % (R12M)", "Net Sales (R12M)", "Net Sales (PY R12M)", "Rolling 12 months vs the prior rolling 12 months.")
add("MoM Change", "IF ( NOT ISBLANK ( [Net Sales (Month)] ), [Net Sales (Month)] - [Net Sales (Prior Month)] )", CUR_VAR, F_PER, "Month-over-month change in net sales ($).")
add("YoY Change (YTD)", "IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Net Sales (YTD)] - [Net Sales (PY YTD)] )", CUR_VAR, F_PER, "Year-to-date change vs last year ($).")
add("GM % pts vs PY (YTD)", "IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Gross Margin % (YTD)] - [Gross Margin % (PY YTD)] )", "+0.0%;-0.0%;0.0%", F_PER, "Change in YTD gross margin % vs last year (percentage points).")
add("GM % pts vs PY (Month)", "IF ( NOT ISBLANK ( [Net Sales (Month)] ), [Gross Margin % (Month)] - [Gross Margin % (PY Month)] )", "+0.0%;-0.0%;0.0%", F_PER, "Change in the reporting month's gross margin % vs the same month last year.")
add("Discount % pts vs PY (YTD)", "IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Discount % (YTD)] - [Discount % (PY YTD)] )", "+0.0%;-0.0%;0.0%", F_PER, "Change in YTD discount depth vs last year (percentage points).")

# ---- 06 Context-based time intelligence (for charts & matrices on the date axis) ----------
add("Net Sales PY", "CALCULATE ( [Net Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )", CUR, F_TI, "Net sales for the same period last year, for whatever dates are in context.")
add("YoY %", "IF ( NOT ISBLANK ( [Net Sales] ), DIVIDE ( [Net Sales] - [Net Sales PY], [Net Sales PY] ) )", PCT_VAR, F_TI, "Year-over-year growth for the dates in context.")
add("Net Sales Prior Period", """
SWITCH (
    TRUE (),
    ISINSCOPE ( 'Date'[Month] ) || ISINSCOPE ( 'Date'[Month Year] ), CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, MONTH ) ),
    ISINSCOPE ( 'Date'[Quarter] ) || ISINSCOPE ( 'Date'[Year Quarter] ), CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, QUARTER ) ),
    CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, YEAR ) )
)""", CUR, F_TI, "Previous month, quarter or year depending on the level shown in the visual.")
add("PoP %", "IF ( NOT ISBLANK ( [Net Sales] ), DIVIDE ( [Net Sales] - [Net Sales Prior Period], [Net Sales Prior Period] ) )", PCT_VAR, F_TI,
    "Period-over-period growth: MoM at month level, QoQ at quarter level, YoY at year level.")
add("Net Sales Running YTD", "IF ( MIN ( 'Date'[Date] ) <= [Last Actual Date], CALCULATE ( [Net Sales], DATESYTD ( 'Date'[Date] ) ) )", CUR, F_TI, "Cumulative year-to-date net sales along a date axis (stops at the last closed month).")
add("Net Sales Running YTD PY", "CALCULATE ( CALCULATE ( [Net Sales], DATESYTD ( 'Date'[Date] ) ), SAMEPERIODLASTYEAR ( 'Date'[Date] ) )", CUR, F_TI, "Prior-year cumulative YTD along a date axis.")
add("Budget Running YTD", "CALCULATE ( [Budget Net Sales], DATESYTD ( 'Date'[Date] ) )", CUR, F_TI, "Cumulative budget along a date axis (full year).")
add("Forecast Running YTD", "CALCULATE ( [Forecast Net Sales], DATESYTD ( 'Date'[Date] ) )", CUR, F_TI, "Cumulative forecast along a date axis (full year).")
add("Net Sales 3M Avg", """
VAR _end = MAX ( 'Date'[Date] )
RETURN
    IF (
        MIN ( 'Date'[Date] ) <= [Last Actual Date],
        CALCULATE ( [Net Sales], DATESINPERIOD ( 'Date'[Date], _end, -3, MONTH ) ) / 3
    )""", CUR, F_TI, "Three-month moving average of net sales.")

# ---- 07 Outlook & KPIs -------------------------------------------------------------------
add("Full Year Outlook", """
VAR _rd = [Reporting Date]
VAR _ytd = CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
VAR _rest = CALCULATE ( [Forecast Net Sales], DATESBETWEEN ( 'Date'[Date], _rd + 1, DATE ( YEAR ( _rd ), 12, 31 ) ) )
RETURN
    IF ( NOT ISBLANK ( _rd ), _ytd + _rest )""", CUR, F_OUT, "Latest estimate for the year: YTD actuals plus forecast for the remaining months.")
add("Full Year Budget", """
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Budget Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), DATE ( YEAR ( _rd ), 12, 31 ) ) )
    )""", CUR, F_OUT, "Full-year budget for the reporting year.")
add("Outlook vs Budget", "[Full Year Outlook] - [Full Year Budget]", CUR_VAR, F_OUT, "Full-year outlook minus full-year budget.")
add("Outlook vs Budget %", "DIVIDE ( [Outlook vs Budget], [Full Year Budget] )", PCT_VAR, F_OUT, "Full-year outlook vs budget, %.")
add("Budget Attainment % (YTD)", "DIVIDE ( [Net Sales (YTD)], [Budget Net Sales (Closed) (YTD)] )", PCT, F_OUT, "YTD actuals as a % of YTD budget.")
add("Full Year Budget Achieved %", "DIVIDE ( [Net Sales (YTD)], [Full Year Budget] )", PCT, F_OUT, "Share of the full-year budget already delivered.")
add("Annualised Run Rate", """
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -3 ) + 1, _rd ) ) * 4
    )""", CUR, F_OUT, "Last three closed months x 4.")
add("Revenue per Customer (YTD)", "DIVIDE ( [Net Sales (YTD)], [Active Customers (YTD)] )", "\\$#,0", F_OUT, "YTD net sales per active customer.")

# ---- 08 Ranking & mix ---------------------------------------------------------------------
add("Product Rank (YTD)", "IF ( ISINSCOPE ( 'Product'[Product] ), RANKX ( ALLSELECTED ( 'Product'[Product] ), [Net Sales (YTD)], , DESC, DENSE ) )", "0", F_RANK, "Rank of the product by YTD net sales within the current selection.")
add("Customer Rank (YTD)", "IF ( ISINSCOPE ( 'Customer'[Customer] ), RANKX ( ALLSELECTED ( 'Customer'[Customer] ), [Net Sales (YTD)], , DESC, DENSE ) )", "0", F_RANK, "Rank of the customer by YTD net sales within the current selection.")
add("Share of Net Sales (YTD)", "DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Product' ) ) )", PCT, F_RANK, "Product/brand/category share of YTD net sales within the current selection.")
add("Channel Share (YTD)", "DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Channel' ) ) )", PCT, F_RANK, "Channel share of YTD net sales.")
add("Region Share (YTD)", "DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Region' ) ) )", PCT, F_RANK, "Region share of YTD net sales.")

# ---- 09 Labels & formatting ---------------------------------------------------------------


def arrow(v, fmt="0.0%", suffix=""):
    return f'IF ( {v} >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( {v} ), "{fmt}" ){suffix}'


add("Report Title", '"Month-End Financial Report"', "", F_UI, "Static report title.")
add("Reporting Period Label", '"Close period  ·  " & FORMAT ( [Reporting Date], "MMMM yyyy" )', "", F_UI, "Dynamic subtitle showing the period being reported.")
add("Data As Of Label", '"Actuals through " & FORMAT ( [Last Actual Date], "d MMM yyyy" ) & "  ·  USD"', "", F_UI, "Footer label with the actuals cut-off.")
add("KPI Label Net Sales (Month)", f"""
VAR _vf = [Var % vs Forecast (Month)]
VAR _yoy = [YoY % (Month)]
RETURN
    IF ( NOT ISBLANK ( _vf ), {arrow("_vf", suffix=' & " vs Fcst    "')} & {arrow("_yoy", suffix=' & " YoY"')} )""", "", F_UI, "Subtitle for the monthly net sales KPI tile.")
add("KPI Label Gross Margin % (Month)", f"""
VAR _vb = [GM % pts vs Budget (Month)]
VAR _py = [GM % pts vs PY (Month)]
RETURN
    IF ( NOT ISBLANK ( _vb ), {arrow("_vb * 100", "0.0", ' & " pp vs Bud    "')} & {arrow("_py * 100", "0.0", ' & " pp YoY"')} )""", "", F_UI, "Subtitle for the gross margin % KPI tile.")
add("KPI Label Net Sales (YTD)", f"""
VAR _yoy = [YoY % (YTD)]
VAR _att = [Budget Attainment % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _yoy ), {arrow("_yoy", suffix=' & " YoY    "')} & FORMAT ( _att, "0.0%" ) & " of budget" )""", "", F_UI, "Subtitle for the YTD net sales KPI tile.")
add("KPI Label Outlook", f"""
VAR _v = [Outlook vs Budget %]
RETURN
    IF ( NOT ISBLANK ( _v ), {arrow("_v", suffix=' & " vs FY budget  (" & FORMAT ( [Full Year Budget], "$#,0.0,,") & "M)"')} )""", "", F_UI, "Subtitle for the full-year outlook KPI tile.")
add("KPI Label Accuracy (Month)", f"""
VAR _a = [Forecast Accuracy % (Month)]
VAR _b = [Forecast Bias % (Month)]
RETURN
    IF ( NOT ISBLANK ( _a ), "Target " & FORMAT ( [Forecast Accuracy Target], "0%" ) & "    Bias " & FORMAT ( _b, "+0.0%;-0.0%" ) )""", "", F_UI, "Subtitle for the forecast accuracy KPI tile.")
add("KPI Label Var vs Forecast (Month)", f"""
VAR _v = [Var % vs Forecast (Month)]
RETURN
    IF ( NOT ISBLANK ( _v ), {arrow("_v", suffix=' & " of forecast  ·  " & FORMAT ( [Forecast Net Sales (Closed) (Month)], "$#,0.00,,") & "M fcst"')} )""", "", F_UI, "Subtitle for the monthly forecast variance tile.")
add("KPI Label Var vs Budget (YTD)", f"""
VAR _v = [Var % vs Budget (YTD)]
RETURN
    IF ( NOT ISBLANK ( _v ), {arrow("_v", suffix=' & " of budget  ·  " & FORMAT ( [Budget Net Sales (Closed) (YTD)], "$#,0.0,,") & "M bud"')} )""", "", F_UI, "Subtitle for the YTD budget variance tile.")
add("KPI Label Accuracy (YTD)", """
VAR _a = [Forecast Accuracy % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _a ), "MAPE (SKU) " & FORMAT ( CALCULATE ( [MAPE %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( [Reporting Date] ), 1, 1 ), [Reporting Date] ) ), "0.0%" ) & "    Target " & FORMAT ( [Forecast Accuracy Target], "0%" ) )""", "", F_UI, "Subtitle for the YTD forecast accuracy tile.")
add("KPI Label Bias (YTD)", """
VAR _b = [Forecast Bias % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _b ), IF ( _b > 0.005, "Over-forecasting", IF ( _b < -0.005, "Under-forecasting", "Unbiased" ) ) & "  ·  ±0.5% tolerance" )""", "", F_UI, "Subtitle for the forecast bias tile.")
add("KPI Label QTD", f"""
VAR _q = [QoQ %]
VAR _y = [YoY % (QTD)]
RETURN
    IF ( NOT ISBLANK ( _q ), {arrow("_q", suffix=' & " QoQ    "')} & {arrow("_y", suffix=' & " YoY"')} )""", "", F_UI, "Subtitle for the QTD tile.")
add("KPI Label YTD YoY", f"""
VAR _y = [YoY % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _y ), {arrow("_y", suffix=' & " vs PY  (" & FORMAT ( [YoY Change (YTD)], "+$#,0.0,,;-$#,0.0,,") & "M)"')} )""", "", F_UI, "Subtitle for the YTD vs PY tile.")
add("KPI Label R12M", f"""
VAR _y = [YoY % (R12M)]
RETURN
    IF ( NOT ISBLANK ( _y ), {arrow("_y", suffix=' & " vs prior 12M  ·  run rate " & FORMAT ( [Annualised Run Rate], "$#,0.0,,") & "M"')} )""", "", F_UI, "Subtitle for the rolling 12M tile.")
add("KPI Label GM % (YTD)", f"""
VAR _p = [GM % pts vs PY (YTD)]
RETURN
    IF ( NOT ISBLANK ( _p ), {arrow("_p * 100", "0.0", ' & " pp vs PY  ·  GM " & FORMAT ( [Gross Margin (YTD)], "$#,0.0,,") & "M"')} )""", "", F_UI, "Subtitle for the YTD gross margin % tile.")
add("KPI Label Discount % (YTD)", f"""
VAR _p = [Discount % pts vs PY (YTD)]
RETURN
    IF ( NOT ISBLANK ( _p ), {arrow("_p * 100", "0.0", ' & " pp vs PY  ·  " & FORMAT ( [Discounts], "$#,0.0,,") & "M all-time"')} )""", "", F_UI, "Subtitle for the YTD discount % tile.")


def color_measure(name, src, good_if_positive=True, tol=0.005, desc=""):
    g, b = (PAL["goodText"], PAL["bad"]) if good_if_positive else (PAL["bad"], PAL["goodText"])
    add(name, f"""
VAR _v = [{src}]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "{PAL['muted']}",
        _v >= {tol}, "{g}",
        _v <= -{tol}, "{b}",
        "{PAL['ink2']}"
    )""", "", F_UI, desc or f"Hex colour for conditional formatting driven by [{src}]: green favourable, red unfavourable, grey within ±{tol:.1%}.")


color_measure("Color Var % vs Forecast", "Var % vs Forecast")
color_measure("Color Var % vs Budget", "Var % vs Budget")
color_measure("Color Var % vs Forecast (Month)", "Var % vs Forecast (Month)")
color_measure("Color Var % vs Budget (YTD)", "Var % vs Budget (YTD)")
color_measure("Color YoY % (Month)", "YoY % (Month)")
color_measure("Color YoY % (YTD)", "YoY % (YTD)")
color_measure("Color YoY %", "YoY %")
color_measure("Color PoP %", "PoP %")
color_measure("Color GM pts vs Budget (Month)", "GM % pts vs Budget (Month)")
color_measure("Color GM pts vs PY (YTD)", "GM % pts vs PY (YTD)")
color_measure("Color Discount pts vs PY (YTD)", "Discount % pts vs PY (YTD)", good_if_positive=False, desc="Hex colour for discount depth change: deeper discounts (positive) are unfavourable.")
color_measure("Color Outlook vs Budget", "Outlook vs Budget %")
color_measure("Color QoQ %", "QoQ %")
color_measure("Color YoY % (R12M)", "YoY % (R12M)")
add("Accuracy vs Target (Month)", "IF ( NOT ISBLANK ( [Forecast Accuracy % (Month)] ), [Forecast Accuracy % (Month)] - [Forecast Accuracy Target] )", "+0.0%;-0.0%;0.0%", F_ACC, "Reporting-month forecast accuracy minus target.")
add("Accuracy vs Target (YTD)", "IF ( NOT ISBLANK ( [Forecast Accuracy % (YTD)] ), [Forecast Accuracy % (YTD)] - [Forecast Accuracy Target] )", "+0.0%;-0.0%;0.0%", F_ACC, "YTD forecast accuracy minus target.")
color_measure("Color Accuracy vs Target (YTD)", "Accuracy vs Target (YTD)", tol=0.0001)
color_measure("Color Accuracy vs Target (Month)", "Accuracy vs Target (Month)", tol=0.0001)
color_measure("Color Var % vs Budget (Month)", "Var % vs Budget (Month)")
color_measure("Color Var % vs Forecast (YTD)", "Var % vs Forecast (YTD)")
add("Color Bias (YTD)", f"""
VAR _b = [Forecast Bias % (YTD)]
RETURN
    IF ( ABS ( _b ) <= 0.005, "{PAL['goodText']}", "{PAL['ink2']}" )""", "", F_UI, "Green when forecast bias is within ±0.5%.")
add("Fill Var vs Forecast", f"""
VAR _v = [Var vs Forecast]
RETURN
    IF ( ISBLANK ( _v ), BLANK (), IF ( _v >= 0, "{PAL['good']}", "{PAL['bad']}" ) )""", "", F_UI, "Bar fill colour for forecast variance: green favourable, red unfavourable.")
add("Fill Var vs Forecast (Month)", f"""
VAR _v = [Var vs Forecast (Month)]
RETURN
    IF ( ISBLANK ( _v ), BLANK (), IF ( _v >= 0, "{PAL['good']}", "{PAL['bad']}" ) )""", "", F_UI, "Bar fill colour for the reporting month's forecast variance.")
add("Fill Accuracy", f"""
VAR _a = [Forecast Accuracy %]
RETURN
    IF ( ISBLANK ( _a ), BLANK (), IF ( _a >= [Forecast Accuracy Target], "{PAL['blue']}", "{PAL['orange']}" ) )""", "", F_UI, "Column fill for forecast accuracy: blue at/above target, orange below.")

MEASURE_NAMES = {m[0] for m in MEASURES}
assert len(MEASURE_NAMES) == len(MEASURES), "duplicate measure names"

# ======================================================================================
# TMDL writer
# ======================================================================================


def indent(text, n):
    pad = "\t" * n
    return "\n".join(pad + line if line.strip() else "" for line in text.split("\n"))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def tmdl_table(tname, spec):
    out = [f"table {q(tname)}"]
    if spec.get("dataCategory"):
        out.append(f"\tdataCategory: {spec['dataCategory']}")
    out.append(f"\tlineageTag: {tag('table', tname)}")
    out.append("")
    if tname == "_Measures":
        for (name, expr, fmt, folder, desc) in MEASURES:
            out.append(f"\t/// {desc}")
            if "\n" in expr:
                out.append(f"\tmeasure {q(name)} =")
                out.append(indent(expr, 3))
            else:
                out.append(f"\tmeasure {q(name)} = {expr}")
            if fmt:
                out.append(f"\t\tformatString: {fmt}")
            out.append(f"\t\tdisplayFolder: {folder}")
            out.append(f"\t\tlineageTag: {tag('measure', name)}")
            out.append("")
    for (cname, dtype, fl) in spec["columns"]:
        out.append(f"\tcolumn {q(cname)}")
        out.append(f"\t\tdataType: {dtype}")
        if fl.get("hidden"):
            out.append("\t\tisHidden")
        if fl.get("key"):
            out.append("\t\tisKey")
        if fl.get("fmt"):
            out.append(f"\t\tformatString: {fl['fmt']}")
        out.append(f"\t\tlineageTag: {tag('column', tname, cname)}")
        out.append(f"\t\tsummarizeBy: {'sum' if fl.get('sum') else 'none'}")
        out.append(f"\t\tsourceColumn: {cname}")
        if fl.get("sortBy"):
            out.append(f"\t\tsortByColumn: {q(fl['sortBy'])}")
        out.append("")
        out.append("\t\tannotation SummarizationSetBy = Automatic")
        out.append("")
    for (cname, dtype, expr, desc) in spec.get("calculated", []):
        out.append(f"\t/// {desc}")
        if "\n" in expr:
            out.append(f"\tcolumn {q(cname)} =")
            out.append(indent(expr, 3))
        else:
            out.append(f"\tcolumn {q(cname)} = {expr}")
        out.append(f"\t\tdataType: {dtype}")
        if dtype == "int64":
            out.append("\t\tformatString: 0")
        out.append(f"\t\tlineageTag: {tag('column', tname, cname)}")
        out.append("\t\tsummarizeBy: none")
        out.append("")
        out.append("\t\tannotation SummarizationSetBy = Automatic")
        out.append("")
    for (hname, levels) in spec.get("hierarchies", []):
        out.append(f"\thierarchy {q(hname)}")
        out.append(f"\t\tlineageTag: {tag('hier', tname, hname)}")
        out.append("")
        for lv in levels:
            out.append(f"\t\tlevel {q(lv)}")
            out.append(f"\t\t\tlineageTag: {tag('level', tname, hname, lv)}")
            out.append(f"\t\t\tcolumn: {q(lv)}")
            out.append("")
    out.append(f"\tpartition {q(tname)} = m")
    out.append("\t\tmode: import")
    out.append(f"\t\tqueryGroup: {spec['group']}")
    out.append("\t\tsource =")
    out.append(indent(M[tname], 4))
    out.append("")
    out.append("\tannotation PBI_ResultType = Table")
    out.append("")
    return "\n".join(out)


def build_semantic_model():
    if os.path.exists(SM):
        shutil.rmtree(SM)
    d = os.path.join(SM, "definition")
    write(os.path.join(SM, "definition.pbism"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}}, indent=2))
    write(os.path.join(SM, ".platform"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": tag("logical", "sm")}}, indent=2))
    write(os.path.join(d, "database.tmdl"), "database\n\tcompatibilityLevel: 1567\n\n")
    order = ["DataFolder"] + list(TABLES)
    model = f"""model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: en-US
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

queryGroup Parameters

\tannotation PBI_QueryGroupOrder = 0

queryGroup Dimensions

\tannotation PBI_QueryGroupOrder = 1

queryGroup Facts

\tannotation PBI_QueryGroupOrder = 2

queryGroup Helpers

\tannotation PBI_QueryGroupOrder = 3

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_QueryOrder = {json.dumps(order)}

annotation PBI_ProTooling = ["DevMode"]

"""
    write(os.path.join(d, "model.tmdl"), model)
    write(os.path.join(d, "expressions.tmdl"), f"""/// Folder that holds the CSV files (must end with a backslash). Change it via Transform data > Edit parameters.
expression DataFolder = "{DATA_FOLDER_DEFAULT}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
\tlineageTag: {tag('expr', 'DataFolder')}
\tqueryGroup: Parameters

\tannotation PBI_ResultType = Text

""")
    rels = []
    for (ft, fc, tt, tc) in RELATIONSHIPS:
        rels.append(f"relationship {tag('rel', ft, fc, tt, tc)}\n\tfromColumn: {q(ft)}.{q(fc)}\n\ttoColumn: {q(tt)}.{q(tc)}\n")
    write(os.path.join(d, "relationships.tmdl"), "\n".join(rels) + "\n")
    for tname, spec in TABLES.items():
        write(os.path.join(d, "tables", f"{tname}.tmdl"), tmdl_table(tname, spec))


# ======================================================================================
# Theme
# ======================================================================================
def solid(c):
    return {"solid": {"color": c}}


THEME = {
    "name": "Aurora FMCG Finance",
    "dataColors": [PAL[k] for k in ["blue", "orange", "aqua", "yellow", "magenta", "green", "violet", "red"]],
    "foreground": PAL["ink"], "foregroundNeutralSecondary": PAL["ink2"], "foregroundNeutralTertiary": PAL["muted"],
    "background": PAL["surface"], "backgroundLight": "#F9F9F7", "backgroundNeutral": PAL["grid"],
    "tableAccent": PAL["blue"], "hyperlink": PAL["blue"], "visitedHyperlink": PAL["violet"],
    "good": PAL["good"], "neutral": PAL["warn"], "bad": PAL["bad"],
    "maximum": "#104281", "center": "#F0EFEC", "minimum": "#D03B3B", "null": "#C3C2B7",
    "textClasses": {
        "callout": {"fontSize": 26, "fontFace": "Segoe UI Semibold", "color": PAL["ink"]},
        "title": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": PAL["ink"]},
        "header": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": PAL["ink"]},
        "label": {"fontSize": 9, "fontFace": "Segoe UI", "color": PAL["ink2"]},
    },
    "visualStyles": {
        "*": {"*": {
            "background": [{"show": True, "color": solid(PAL["surface"]), "transparency": 0}],
            "border": [{"show": True, "color": solid("#E6E5DF"), "radius": 10, "width": 1}],
            "dropShadow": [{"show": True, "color": solid("#0B0B0B"), "position": "Outer", "preset": "Custom",
                            "shadowSpread": 0, "shadowBlur": 12, "angle": 90, "shadowDistance": 2, "transparency": 93}],
            "padding": [{"top": 10, "bottom": 10, "left": 14, "right": 14}],
            "title": [{"show": True, "fontColor": solid(PAL["ink"]), "fontSize": 11, "fontFamily": "Segoe UI Semibold", "alignment": "left"}],
            "subTitle": [{"fontColor": solid(PAL["muted"]), "fontSize": 9, "fontFamily": "Segoe UI"}],
            "visualHeader": [{"show": True, "foreground": solid(PAL["muted"]), "transparency": 100}],
            "valueAxis": [{"labelColor": solid(PAL["muted"]), "fontSize": 9, "gridlineShow": True, "gridlineColor": solid("#ECEBE6"),
                           "gridlineThickness": 1, "gridlineStyle": "solid", "showAxisTitle": False}],
            "categoryAxis": [{"labelColor": solid(PAL["muted"]), "fontSize": 9, "showAxisTitle": False, "gridlineShow": False}],
            "legend": [{"show": True, "position": "TopRight", "labelColor": solid(PAL["ink2"]), "fontSize": 9, "showTitle": False}],
            "labels": [{"color": solid(PAL["ink2"]), "fontSize": 9}],
        }},
        "page": {"*": {
            "background": [{"color": solid(PAL["page"]), "transparency": 0}],
            "outspace": [{"color": solid(PAL["page"]), "transparency": 0}],
        }},
        "card": {"*": {
            "labels": [{"color": solid(PAL["ink"]), "fontSize": 24, "fontFamily": "Segoe UI Semibold"}],
            "categoryLabels": [{"show": False}],
            "title": [{"fontSize": 10, "fontColor": solid(PAL["ink2"]), "fontFamily": "Segoe UI Semibold"}],
        }},
        "slicer": {"*": {
            "header": [{"fontColor": solid(PAL["ink2"]), "fontSize": 9, "fontFamily": "Segoe UI Semibold"}],
            "items": [{"fontColor": solid(PAL["ink"]), "fontSize": 10}],
            "dropShadow": [{"show": False}],
            "padding": [{"top": 4, "bottom": 4, "left": 8, "right": 8}],
        }},
        "lineChart": {"*": {"lineStyles": [{"strokeWidth": 2, "showMarker": False}]}},
        "pivotTable": {"*": {
            "columnHeaders": [{"fontColor": solid(PAL["ink2"]), "backColor": solid("#F4F3EF"), "fontFamily": "Segoe UI Semibold", "fontSize": 9, "wordWrap": True}],
            "rowHeaders": [{"fontColor": solid(PAL["ink"]), "fontSize": 9}],
            "values": [{"fontColor": solid(PAL["ink"]), "fontSize": 9, "backColorPrimary": solid("#FFFFFF"), "backColorSecondary": solid("#FAFAF8")}],
            "total": [{"fontColor": solid(PAL["ink"]), "fontFamily": "Segoe UI Semibold", "backColor": solid("#F4F3EF")}],
            "grid": [{"gridHorizontal": True, "gridHorizontalColor": solid("#ECEBE6"), "gridVertical": False, "rowPadding": 4}],
        }},
        "tableEx": {"*": {
            "columnHeaders": [{"fontColor": solid(PAL["ink2"]), "backColor": solid("#F4F3EF"), "fontFamily": "Segoe UI Semibold", "fontSize": 9}],
            "values": [{"fontColor": solid(PAL["ink"]), "fontSize": 9, "backColorPrimary": solid("#FFFFFF"), "backColorSecondary": solid("#FAFAF8")}],
            "total": [{"fontColor": solid(PAL["ink"]), "fontFamily": "Segoe UI Semibold", "backColor": solid("#F4F3EF")}],
            "grid": [{"gridHorizontal": True, "gridHorizontalColor": solid("#ECEBE6"), "gridVertical": False, "rowPadding": 4}],
        }},
        "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}]}},
        "waterfallChart": {"*": {"sentimentColors": [{"increaseFill": solid(PAL["good"]), "decreaseFill": solid(PAL["bad"]), "totalFill": solid(PAL["blue"])}]}},
    },
}

# ======================================================================================
# Report (PBIR)
# ======================================================================================
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
VC_SCHEMA = f"{SCHEMA}/visualContainer/2.4.0/schema.json"
MEAS = "_Measures"


def lit(v):
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, int):
        s = f"{v}L"
    elif isinstance(v, float):
        s = f"{v}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def mref(name):
    assert name in MEASURE_NAMES, f"unknown measure {name}"
    return {"Measure": {"Expression": {"SourceRef": {"Entity": MEAS}}, "Property": name}}


def cref(table, col):
    return {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}


def field(f):
    """'Table[Column]' or a measure name."""
    if "[" in f:
        t, c = f[:-1].split("[")
        return cref(t, c), f"{t}.{c}", c
    return mref(f), f"{MEAS}.{f}", f


def proj(f, display=None):
    fld, qref, native = field(f)
    p = {"field": fld, "queryRef": qref, "nativeQueryRef": native}
    if display:
        p["displayName"] = display
    return p


def color_expr(measure):
    return {"solid": {"color": {"expr": mref(measure)}}}


def color_lit(c):
    return {"solid": {"color": lit(c)}}


def title_objs(title, subtitle=None, show=True):
    o = {"title": [{"properties": {"show": lit(show), "text": lit(title)}}]} if title is not None else {}
    if subtitle:
        o["subTitle"] = [{"properties": {"show": lit(True), "text": lit(subtitle)}}]
    return o


def offset_filter(name, lo, hi, column="Month Offset"):
    col = {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": column}}
    return {
        "name": name,
        "field": cref("Date", column),
        "type": "Advanced",
        "filter": {
            "Version": 2,
            "From": [{"Name": "d", "Entity": "Date", "Type": 0}],
            "Where": [{"Condition": {"And": {
                "Left": {"Comparison": {"ComparisonKind": 2, "Left": col, "Right": {"Literal": {"Value": f"{lo}L"}}}},
                "Right": {"Comparison": {"ComparisonKind": 4, "Left": col, "Right": {"Literal": {"Value": f"{hi}L"}}}},
            }}}],
        },
        "howCreated": "User",
    }


def eq_filter(name, column, value):
    col = {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": column}}
    return {
        "name": name,
        "field": cref("Date", column),
        "type": "Advanced",
        "filter": {
            "Version": 2,
            "From": [{"Name": "d", "Entity": "Date", "Type": 0}],
            "Where": [{"Condition": {"Comparison": {"ComparisonKind": 0, "Left": col, "Right": {"Literal": {"Value": f"{value}L"}}}}}],
        },
        "howCreated": "User",
    }


class Page:
    def __init__(self, name, display):
        self.name, self.display, self.visuals, self.z = name, display, [], 1000

    def add(self, vname, vtype, x, y, w, h, query=None, objects=None, vco=None, filters=None, sort=None, z=None):
        self.z += 1
        visual = {"visualType": vtype}
        if query:
            qs = {}
            for role, fields in query.items():
                qs[role] = {"projections": [proj(*f) if isinstance(f, tuple) else proj(f) for f in fields]}
            visual["query"] = {"queryState": qs}
            if sort:
                fld = field(sort[0])[0]
                visual["query"]["sortDefinition"] = {"sort": [{"field": fld, "direction": sort[1]}], "isDefaultSort": False}
        if objects:
            visual["objects"] = objects
        if vco:
            visual["visualContainerObjects"] = vco
        if vtype not in ("textbox",):
            visual["drillFilterOtherVisuals"] = True
        vc = {"$schema": VC_SCHEMA, "name": vname,
              "position": {"x": x, "y": y, "z": z if z is not None else self.z, "width": w, "height": h, "tabOrder": self.z},
              "visual": visual}
        if filters:
            vc["filterConfig"] = {"filters": filters}
        self.visuals.append(vc)


def textbox(page, vname, x, y, w, h, runs):
    paragraphs = []
    for para in runs:
        paragraphs.append({"textRuns": [{"value": t, "textStyle": s} for (t, s) in para]})
    page.add(vname, "textbox", x, y, w, h,
             objects={"general": [{"properties": {"paragraphs": paragraphs}}]},
             vco={"background": [{"properties": {"show": lit(False)}}], "border": [{"properties": {"show": lit(False)}}],
                  "dropShadow": [{"properties": {"show": lit(False)}}]})


def header(page, title, subtitle):
    textbox(page, "hdrTitle", 8, 6, 470, 60, [
        [(title, {"fontFamily": "Segoe UI Semibold", "fontSize": "20pt", "color": PAL["ink"]})],
        [(subtitle, {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": PAL["muted"]})],
    ])
    slicers = [("slYear", "Date[Year]", "Year"), ("slMonth", "Date[Month]", "Month"), ("slRegion", "Region[Region]", "Region"),
               ("slChannel", "Channel[Channel]", "Channel"), ("slCategory", "Product[Category]", "Category")]
    x = 488
    for vname, f, label in slicers:
        page.add(vname, "slicer", x, 12, 106, 50, query={"Values": [f]},
                 objects={"data": [{"properties": {"mode": lit("Dropdown")}}],
                          "header": [{"properties": {"show": lit(True), "text": lit(label)}}],
                          "selection": [{"properties": {"singleSelect": lit(label in ("Year", "Month")), "selectAllCheckboxEnabled": lit(label not in ("Year", "Month"))}}]},
                 vco={"dropShadow": [{"properties": {"show": lit(False)}}]})
        x += 114
    page.add("hdrPeriod", "card", 1060, 12, 204, 50, query={"Values": ["Reporting Period Label"]},
             objects={"labels": [{"properties": {"fontSize": lit(11.0), "color": color_lit("#FFFFFF"), "fontFamily": lit("Segoe UI Semibold")}}],
                      "categoryLabels": [{"properties": {"show": lit(True), "color": color_lit("#C9D3E3"), "fontSize": lit(8.0)}}]},
             vco={"title": [{"properties": {"show": lit(False)}}],
                  "background": [{"properties": {"show": lit(True), "color": color_lit(PAL["navy"]), "transparency": lit(0.0)}}],
                  "border": [{"properties": {"show": lit(False)}}]})
    page.add("ftrAsOf", "card", 1000, 700, 270, 20, query={"Values": ["Data As Of Label"]},
             objects={"labels": [{"properties": {"fontSize": lit(8.0), "color": color_lit(PAL["muted"]), "fontFamily": lit("Segoe UI")}}],
                      "categoryLabels": [{"properties": {"show": lit(False)}}]},
             vco={"title": [{"properties": {"show": lit(False)}}], "background": [{"properties": {"show": lit(False)}}],
                  "border": [{"properties": {"show": lit(False)}}], "dropShadow": [{"properties": {"show": lit(False)}}],
                  "padding": [{"properties": {"top": lit(0.0), "bottom": lit(0.0), "left": lit(0.0), "right": lit(0.0)}}]})


def kpi_tile(page, i, x, y, w, title, value_measure, label_measure, color_measure=None):
    page.add(f"kpi{i}Value", "card", x, y, w, 106, query={"Values": [value_measure]},
             objects={"labels": [{"properties": {"fontSize": lit(24.0)}}], "categoryLabels": [{"properties": {"show": lit(False)}}]},
             vco={**title_objs(title), "padding": [{"properties": {"top": lit(8.0), "bottom": lit(30.0), "left": lit(14.0), "right": lit(14.0)}}]})
    lab = {"fontSize": lit(9.0), "fontFamily": lit("Segoe UI Semibold")}
    lab["color"] = color_expr(color_measure) if color_measure else color_lit(PAL["ink2"])
    page.add(f"kpi{i}Label", "card", x + 6, y + 72, w - 12, 30, query={"Values": [label_measure]},
             objects={"labels": [{"properties": lab}], "categoryLabels": [{"properties": {"show": lit(False)}}]},
             vco={"title": [{"properties": {"show": lit(False)}}], "background": [{"properties": {"show": lit(False)}}],
                  "border": [{"properties": {"show": lit(False)}}], "dropShadow": [{"properties": {"show": lit(False)}}],
                  "padding": [{"properties": {"top": lit(0.0), "bottom": lit(0.0), "left": lit(8.0), "right": lit(8.0)}}]},
             z=5000 + page.z)


def kpi_row(page, tiles):
    n = len(tiles)
    gap = 12
    w = (1248 - gap * (n - 1)) // n
    for i, t in enumerate(tiles):
        kpi_tile(page, i + 1, 16 + i * (w + gap), 76, w, *t)


def series_colors(mapping):
    return [{"properties": {"fill": color_lit(c)}, "selector": {"metadata": field(m)[1]}} for m, c in mapping.items()]


def fx_font(measure_qref, color_measure):
    return {"properties": {"fontColor": color_expr(color_measure)},
            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": field(measure_qref)[1]}}


def build_pages():
    pages = []

    # ---------------------------------------------------------------- 1. Executive summary
    p = Page("p01_ExecutiveSummary", "Executive Summary")
    header(p, "Executive Summary", "Aurora Consumer Goods  ·  FMCG month-end close")
    kpi_row(p, [
        ("Net Sales · Month", "Net Sales (Month)", "KPI Label Net Sales (Month)", "Color Var % vs Forecast (Month)"),
        ("Gross Margin % · Month", "Gross Margin % (Month)", "KPI Label Gross Margin % (Month)", "Color GM pts vs Budget (Month)"),
        ("Net Sales · YTD", "Net Sales (YTD)", "KPI Label Net Sales (YTD)", "Color YoY % (YTD)"),
        ("Full-Year Outlook", "Full Year Outlook", "KPI Label Outlook", "Color Outlook vs Budget"),
        ("Forecast Accuracy · Month", "Forecast Accuracy % (Month)", "KPI Label Accuracy (Month)", "Color Accuracy vs Target (Month)"),
    ])
    p.add("trend", "lineChart", 16, 194, 820, 262,
          query={"Category": ["Date[Month Year]"], "Y": ["Net Sales", "Forecast Net Sales", "Budget Net Sales"]},
          objects={"dataPoint": series_colors({"Net Sales": ACTUAL, "Forecast Net Sales": FORECAST, "Budget Net Sales": BUDGET}),
                   "lineStyles": [{"properties": {"strokeWidth": lit(3)}, "selector": {"metadata": f"{MEAS}.Net Sales"}},
                                  {"properties": {"lineStyle": lit("dashed")}, "selector": {"metadata": f"{MEAS}.Forecast Net Sales"}},
                                  {"properties": {"lineStyle": lit("dotted")}, "selector": {"metadata": f"{MEAS}.Budget Net Sales"}}]},
          vco=title_objs("Net sales: actual vs forecast vs budget", "Last 13 closed months + 2 forecast months"),
          filters=[offset_filter("fTrendWindow", -12, 2)], sort=("Date[Month Year]", "Ascending"))
    p.add("bridge", "waterfallChart", 848, 194, 416, 262,
          query={"Category": ["Variance Bridge[Step]"], "Y": [("Bridge Value (YTD)", "Net sales")]},
          objects={"labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000000.0), "labelPrecision": lit(1)}}]},
          vco=title_objs("YTD bridge: budget → actual", "Volume & mix vs price & discount; total = actual"),
          sort=("Variance Bridge[Step]", "Ascending"))
    p.add("catBar", "clusteredBarChart", 16, 468, 404, 228,
          query={"Category": ["Product[Category]"], "Y": [("Net Sales (YTD)", "Net sales YTD")]},
          objects={"dataPoint": [{"properties": {"fill": color_lit(ACTUAL)}}],
                   "labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000000.0), "labelPrecision": lit(1)}}]},
          vco=title_objs("Net sales YTD by category"), sort=("Net Sales (YTD)", "Descending"))
    p.add("regionMatrix", "pivotTable", 432, 468, 500, 228,
          query={"Rows": ["Region[Region]"],
                 "Values": [("Net Sales (Month)", "Month"), ("Var % vs Forecast (Month)", "vs Fcst"), ("YoY % (Month)", "YoY"),
                            ("Net Sales (YTD)", "YTD"), ("Var % vs Budget (YTD)", "YTD vs Bud"), ("Gross Margin % (YTD)", "GM % YTD")]},
          objects={"values": [fx_font("Var % vs Forecast (Month)", "Color Var % vs Forecast (Month)"),
                              fx_font("YoY % (Month)", "Color YoY % (Month)"),
                              fx_font("Var % vs Budget (YTD)", "Color Var % vs Budget (YTD)")]},
          vco=title_objs("Regional scorecard"), sort=("Net Sales (YTD)", "Descending"))
    p.add("channelBar", "clusteredBarChart", 944, 468, 320, 228,
          query={"Category": ["Channel[Channel]"], "Y": [("Channel Share (YTD)", "Share of net sales YTD")]},
          objects={"dataPoint": [{"properties": {"fill": color_lit(ACTUAL)}}],
                   "labels": [{"properties": {"show": lit(True)}}]},
          vco=title_objs("Channel mix · YTD"), sort=("Channel Share (YTD)", "Descending"))
    pages.append(p)

    # ---------------------------------------------------------------- 2. Variance analysis
    p = Page("p02_VarianceAnalysis", "Variance Analysis")
    header(p, "Actual vs Forecast & Budget", "Variance analysis  ·  favourable = green, unfavourable = red")
    kpi_row(p, [
        ("Variance vs Forecast · Month", "Var vs Forecast (Month)", "KPI Label Var vs Forecast (Month)", "Color Var % vs Forecast (Month)"),
        ("Variance vs Budget · YTD", "Var vs Budget (YTD)", "KPI Label Var vs Budget (YTD)", "Color Var % vs Budget (YTD)"),
        ("Forecast Accuracy · YTD", "Forecast Accuracy % (YTD)", "KPI Label Accuracy (YTD)", "Color Accuracy vs Target (YTD)"),
        ("Forecast Bias · YTD", "Forecast Bias % (YTD)", "KPI Label Bias (YTD)", "Color Bias (YTD)"),
    ])
    p.add("varTrend", "clusteredColumnChart", 16, 194, 620, 250,
          query={"Category": ["Date[Month Year]"], "Y": [("Var vs Forecast", "Variance vs forecast")]},
          objects={"dataPoint": [{"properties": {"fill": color_expr("Fill Var vs Forecast")},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                   "labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000.0), "labelPrecision": lit(0)}}]},
          vco=title_objs("Monthly variance vs forecast", "Last 13 closed months"),
          filters=[offset_filter("fVarWindow", -12, 0)], sort=("Date[Month Year]", "Ascending"))
    p.add("accTrend", "lineChart", 648, 194, 616, 250,
          query={"Category": ["Date[Month Year]"], "Y": [("Forecast Accuracy %", "Accuracy (1 - WMAPE)"), ("Forecast Accuracy Target", "Target")]},
          objects={"dataPoint": series_colors({"Forecast Accuracy %": ACTUAL, "Forecast Accuracy Target": PRIOR}),
                   "lineStyles": [{"properties": {"lineStyle": lit("dashed"), "strokeWidth": lit(1)}, "selector": {"metadata": f"{MEAS}.Forecast Accuracy Target"}}],
                   "valueAxis": [{"properties": {"start": lit(0.85), "end": lit(1.0)}}]},
          vco=title_objs("Forecast accuracy trend", "SKU x region x month, weighted by net sales"),
          filters=[offset_filter("fAccWindow", -12, 0)], sort=("Date[Month Year]", "Ascending"))
    p.add("varMatrix", "pivotTable", 16, 456, 820, 240,
          query={"Rows": ["Product[Category]", "Product[Brand]", "Product[Product]"],
                 "Values": [("Net Sales (Month)", "Actual"), ("Forecast Net Sales (Closed) (Month)", "Forecast"),
                            ("Var vs Forecast (Month)", "Var"), ("Var % vs Forecast (Month)", "Var %"),
                            ("Budget Net Sales (Closed) (Month)", "Budget"), ("Var vs Budget (Month)", "Var vs Bud"),
                            ("Var % vs Budget (Month)", "Var % Bud")]},
          objects={"values": [fx_font("Var vs Forecast (Month)", "Color Var % vs Forecast (Month)"),
                              fx_font("Var % vs Forecast (Month)", "Color Var % vs Forecast (Month)"),
                              fx_font("Var vs Budget (Month)", "Color Var % vs Budget (Month)"),
                              fx_font("Var % vs Budget (Month)", "Color Var % vs Budget (Month)")]},
          vco=title_objs("Reporting month variance by category › brand › SKU", "Expand rows to drill down"),
          sort=("Net Sales (Month)", "Descending"))
    p.add("varRegion", "clusteredBarChart", 848, 456, 416, 116,
          query={"Category": ["Region[Region]"], "Y": [("Var vs Forecast (Month)", "Variance vs forecast")]},
          objects={"dataPoint": [{"properties": {"fill": color_expr("Fill Var vs Forecast (Month)")},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                   "labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000.0)}}]},
          vco=title_objs("Month variance vs forecast by region"), sort=("Var vs Forecast (Month)", "Descending"))
    p.add("varChannel", "clusteredBarChart", 848, 580, 416, 116,
          query={"Category": ["Channel[Channel]"], "Y": [("Var vs Forecast (Month)", "Variance vs forecast")]},
          objects={"dataPoint": [{"properties": {"fill": color_expr("Fill Var vs Forecast (Month)")},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                   "labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000.0)}}]},
          vco=title_objs("Month variance vs forecast by channel"), sort=("Var vs Forecast (Month)", "Descending"))
    pages.append(p)

    # ---------------------------------------------------------------- 3. Monthly & quarterly KPIs
    p = Page("p03_PeriodKPIs", "Monthly & Quarterly KPIs")
    header(p, "Monthly & Quarterly KPIs", "Time intelligence  ·  MoM, QoQ, YoY, YTD, rolling 12 months")
    kpi_row(p, [
        ("Net Sales · QTD", "Net Sales (QTD)", "KPI Label QTD", "Color QoQ %"),
        ("Net Sales · YTD", "Net Sales (YTD)", "KPI Label YTD YoY", "Color YoY % (YTD)"),
        ("Net Sales · Rolling 12M", "Net Sales (R12M)", "KPI Label R12M", "Color YoY % (R12M)"),
        ("Gross Margin % · YTD", "Gross Margin % (YTD)", "KPI Label GM % (YTD)", "Color GM pts vs PY (YTD)"),
        ("Discount % · YTD", "Discount % (YTD)", "KPI Label Discount % (YTD)", "Color Discount pts vs PY (YTD)"),
    ])
    p.add("ytdRace", "lineChart", 16, 194, 620, 250,
          query={"Category": ["Date[Month]"], "Y": [("Net Sales Running YTD", "Actual YTD"), ("Budget Running YTD", "Budget YTD"),
                                                     ("Forecast Running YTD", "Forecast YTD"), ("Net Sales Running YTD PY", "Prior year YTD")]},
          objects={"dataPoint": series_colors({"Net Sales Running YTD": ACTUAL, "Budget Running YTD": BUDGET,
                                               "Forecast Running YTD": FORECAST, "Net Sales Running YTD PY": PRIOR}),
                   "lineStyles": [{"properties": {"strokeWidth": lit(3)}, "selector": {"metadata": f"{MEAS}.Net Sales Running YTD"}},
                                  {"properties": {"lineStyle": lit("dashed")}, "selector": {"metadata": f"{MEAS}.Forecast Running YTD"}},
                                  {"properties": {"lineStyle": lit("dotted")}, "selector": {"metadata": f"{MEAS}.Budget Running YTD"}}]},
          vco=title_objs("Cumulative net sales: current year", "Actual vs forecast, budget and prior year"),
          filters=[eq_filter("fCurrentYear", "Year Offset", 0)], sort=("Date[Month]", "Ascending"))
    p.add("qtrColumns", "clusteredColumnChart", 648, 194, 616, 250,
          query={"Category": ["Date[Quarter]"], "Series": ["Date[Year]"], "Y": [("Net Sales", "Net sales")]},
          objects={"labels": [{"properties": {"show": lit(True), "labelDisplayUnits": lit(1000000.0), "labelPrecision": lit(1)}}]},
          vco=title_objs("Quarterly net sales by year", "Like-for-like quarter comparison"),
          sort=("Date[Quarter]", "Ascending"))
    p.add("kpiMatrix", "pivotTable", 16, 456, 820, 240,
          query={"Rows": ["Date[Year]", "Date[Quarter]", "Date[Month]"],
                 "Values": [("Net Sales", "Net sales"), ("PoP %", "PoP %"), ("YoY %", "YoY %"), ("Gross Margin %", "GM %"),
                            ("Discount %", "Disc %"), ("Units Sold", "Units"), ("Avg Net Price", "Net price"),
                            ("Var % vs Budget", "vs Budget"), ("Forecast Accuracy %", "Fcst acc.")]},
          objects={"values": [fx_font("PoP %", "Color PoP %"), fx_font("YoY %", "Color YoY %"),
                              fx_font("Var % vs Budget", "Color Var % vs Budget")]},
          vco=title_objs("Period KPI table", "Year › quarter › month; PoP = MoM at month, QoQ at quarter, YoY at year"),
          sort=("Date[Year]", "Descending"))
    p.add("gmTrend", "lineChart", 848, 456, 416, 240,
          query={"Category": ["Date[Month Year]"], "Y": [("Gross Margin %", "Actual GM %"), ("Budget Gross Margin %", "Budget GM %")]},
          objects={"dataPoint": series_colors({"Gross Margin %": ACTUAL, "Budget Gross Margin %": BUDGET}),
                   "lineStyles": [{"properties": {"lineStyle": lit("dotted")}, "selector": {"metadata": f"{MEAS}.Budget Gross Margin %"}}]},
          vco=title_objs("Gross margin % vs budget", "Last 13 closed months"),
          filters=[offset_filter("fGmWindow", -12, 0)], sort=("Date[Month Year]", "Ascending"))
    pages.append(p)

    # ---------------------------------------------------------------- 4. Product & region drilldown
    p = Page("p04_ProductRegion", "Product & Region Drilldown")
    header(p, "Product & Region Drilldown", "Portfolio, regional and customer performance  ·  YTD")
    p.add("prodMatrix", "pivotTable", 16, 76, 720, 330,
          query={"Rows": ["Product[Category]", "Product[Brand]", "Product[Product]"],
                 "Values": [("Net Sales (YTD)", "Net sales YTD"), ("Share of Net Sales (YTD)", "Share"), ("YoY % (YTD)", "YoY"),
                            ("Gross Margin % (YTD)", "GM %"), ("Var % vs Forecast (YTD)", "vs Fcst"), ("Var % vs Budget (YTD)", "vs Bud"),
                            ("Units Sold (YTD)", "Units")]},
          objects={"values": [fx_font("YoY % (YTD)", "Color YoY % (YTD)"),
                              fx_font("Var % vs Forecast (YTD)", "Color Var % vs Forecast (YTD)"),
                              fx_font("Var % vs Budget (YTD)", "Color Var % vs Budget (YTD)")]},
          vco=title_objs("Portfolio performance", "Category › brand › SKU  ·  expand to drill"),
          sort=("Net Sales (YTD)", "Descending"))
    p.add("portfolio", "scatterChart", 748, 76, 516, 330,
          query={"Category": ["Product[Product]"], "X": [("YoY % (YTD)", "YoY growth")], "Y": [("Gross Margin % (YTD)", "Gross margin %")],
                 "Size": [("Net Sales (YTD)", "Net sales YTD")]},
          objects={"dataPoint": [{"properties": {"fill": color_lit(ACTUAL)}}]},
          vco=title_objs("SKU portfolio: growth vs margin", "Bubble size = YTD net sales"))
    p.add("regionBar", "clusteredBarChart", 16, 418, 400, 278,
          query={"Category": ["Region[Region]"], "Y": [("Net Sales (YTD)", "Net sales YTD"), ("Net Sales (PY YTD)", "Prior year YTD")]},
          objects={"dataPoint": series_colors({"Net Sales (YTD)": ACTUAL, "Net Sales (PY YTD)": PRIOR})},
          vco=title_objs("Region: YTD vs prior year"), sort=("Net Sales (YTD)", "Descending"))
    p.add("regionChannel", "pivotTable", 428, 418, 420, 278,
          query={"Rows": ["Region[Region]"], "Columns": ["Channel[Channel Group]"], "Values": [("Net Sales (YTD)", "Net sales YTD")]},
          vco=title_objs("Region × channel group · YTD"))
    p.add("topCustomers", "tableEx", 860, 418, 404, 278,
          query={"Values": [("Customer Rank (YTD)", "#"), "Customer[Customer]", ("Net Sales (YTD)", "Net sales YTD"),
                            ("YoY % (YTD)", "YoY"), ("Gross Margin % (YTD)", "GM %")]},
          objects={"values": [fx_font("YoY % (YTD)", "Color YoY % (YTD)")]},
          vco=title_objs("Customer ranking · YTD"), sort=("Net Sales (YTD)", "Descending"))
    pages.append(p)
    return pages


def build_report():
    if os.path.exists(RP):
        shutil.rmtree(RP)
    write(os.path.join(RP, "definition.pbir"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}}, indent=2))
    write(os.path.join(RP, ".platform"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": tag("logical", "rpt")}}, indent=2))
    d = os.path.join(RP, "definition")
    write(os.path.join(d, "version.json"), json.dumps({"$schema": f"{SCHEMA}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, indent=2))
    theme_file = "Aurora_FMCG_Theme.json"
    write(os.path.join(d, "report.json"), json.dumps({
        "$schema": f"{SCHEMA}/report/2.0.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"},
            "customTheme": {"name": theme_file, "reportVersionAtImport": "5.61", "type": "RegisteredResources"},
        },
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": theme_file, "path": theme_file, "type": "CustomTheme"}]},
        ],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True, "useEnhancedTooltips": True},
    }, indent=2))
    theme_json = json.dumps(THEME, indent=2, ensure_ascii=False)
    write(os.path.join(RP, "StaticResources", "RegisteredResources", theme_file), theme_json)
    # Base theme: a neutral copy of the custom theme so the report is self-contained
    base = dict(THEME)
    base["name"] = "CY24SU10"
    write(os.path.join(RP, "StaticResources", "SharedResources", "BaseThemes", "CY24SU10.json"), json.dumps(base, indent=2, ensure_ascii=False))
    write(os.path.join(ROOT, "theme", theme_file), theme_json)

    pages = build_pages()
    write(os.path.join(d, "pages", "pages.json"), json.dumps({
        "$schema": f"{SCHEMA}/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p.name for p in pages], "activePageName": pages[0].name}, indent=2))
    for p in pages:
        write(os.path.join(d, "pages", p.name, "page.json"), json.dumps({
            "$schema": f"{SCHEMA}/page/2.0.0/schema.json",
            "name": p.name, "displayName": p.display, "displayOption": "FitToPage", "height": 720, "width": 1280}, indent=2))
        names = set()
        for v in p.visuals:
            assert v["name"] not in names
            names.add(v["name"])
            write(os.path.join(d, "pages", p.name, "visuals", v["name"], "visual.json"), json.dumps(v, indent=2, ensure_ascii=False))
    return pages


def build_pbip_file():
    write(os.path.join(PBIP, f"{NAME}.pbip"), json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
        "settings": {"enableAutoRecovery": True}}, indent=2))
    write(os.path.join(PBIP, ".gitignore"), "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")


# ======================================================================================
# Companion artefacts
# ======================================================================================
def build_companions():
    pq = os.path.join(ROOT, "powerquery")
    if os.path.exists(pq):
        shutil.rmtree(pq)
    write(os.path.join(pq, "00_DataFolder (parameter).pq"),
          f'// Text parameter. Point it at the folder holding the CSVs (keep the trailing backslash).\n"{DATA_FOLDER_DEFAULT}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n')
    for i, (t, code) in enumerate(M.items(), start=1):
        write(os.path.join(pq, f"{i:02d}_{t.replace(' ', '')}.pq"), f"// Query: {t}\n{code}\n")

    lines = ["// FMCG Month-End Financial Reporting - DAX measure library",
             "// Paste into Power BI Desktop > DAX query view (or Tabular Editor) and choose 'Update model with changes'",
             "// to (re)create every measure in the _Measures table.", "", "DEFINE"]
    cur = None
    for (name, expr, fmt, folder, desc) in MEASURES:
        if folder != cur:
            lines += ["", f"    // ===== {folder} ====="]
            cur = folder
        lines.append(f"    /// {desc}")
        body = expr.replace("\n", "\n        ")
        lines.append(f"    MEASURE '_Measures'[{name}] =\n        {body}")
    lines += ["", "EVALUATE", "    ROW (", '        "Net Sales (Month)", [Net Sales (Month)],', '        "Var % vs Forecast (Month)", [Var % vs Forecast (Month)],',
              '        "Net Sales (YTD)", [Net Sales (YTD)],', '        "YoY % (YTD)", [YoY % (YTD)],', '        "Forecast Accuracy % (YTD)", [Forecast Accuracy % (YTD)]', "    )", ""]
    write(os.path.join(ROOT, "dax", "measures.dax"), "\n".join(lines))

    md = ["# DAX measure library", "",
          f"{len(MEASURES)} measures live in the `_Measures` table, grouped into display folders. "
          "This file is generated from `scripts/build_pbip.py`, the same source as the TMDL model.", "",
          "## How the reporting period works", "",
          "Every measure with a `(Month)`, `(QTD)`, `(YTD)`, `(R12M)` or `(PY …)` suffix is anchored on **[Reporting Date]**: "
          "the end of the period selected in the Year/Month slicers, capped at the last closed month (the latest month with actuals). "
          "With no selection the report shows the latest close, so it rolls forward automatically when next month's actuals land.", "",
          "Measures without a suffix (`Net Sales`, `YoY %`, `PoP %`, `Net Sales Running YTD` …) follow the filter context, so they "
          "are the ones to put on a date axis or in a Year › Quarter › Month matrix.", "",
          "Forecast and budget comparisons use the `(Closed)` versions, which only include months that have actuals, so a "
          "year-to-date variance never compares 10 months of actuals against 12 months of plan.", ""]
    cur = None
    for (name, expr, fmt, folder, desc) in MEASURES:
        if folder != cur:
            md += ["", f"## {folder}", ""]
            cur = folder
        md += [f"### {name}", "", desc, "", "```dax", f"{name} =", expr, "```", ""]
    write(os.path.join(ROOT, "docs", "dax-measure-library.md"), "\n".join(md))


if __name__ == "__main__":
    build_semantic_model()
    pages = build_report()
    build_pbip_file()
    build_companions()
    nv = sum(len(p.visuals) for p in pages)
    print(f"measures={len(MEASURES)} tables={len(TABLES)} relationships={len(RELATIONSHIPS)} pages={len(pages)} visuals={nv}")
