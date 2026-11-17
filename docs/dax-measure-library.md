# DAX measure library

182 measures live in the `_Measures` table, grouped into display folders. This file is generated from `scripts/build_pbip.py`, the same source as the TMDL model.

## How the reporting period works

Every measure with a `(Month)`, `(QTD)`, `(YTD)`, `(R12M)` or `(PY …)` suffix is anchored on **[Reporting Date]**: the end of the period selected in the Year/Month slicers, capped at the last closed month (the latest month with actuals). With no selection the report shows the latest close, so it rolls forward automatically when next month's actuals land.

Measures without a suffix (`Net Sales`, `YoY %`, `PoP %`, `Net Sales Running YTD` …) follow the filter context, so they are the ones to put on a date axis or in a Year › Quarter › Month matrix.

Forecast and budget comparisons use the `(Closed)` versions, which only include months that have actuals, so a year-to-date variance never compares 10 months of actuals against 12 months of plan.


## 01 Actuals

### Gross Sales

Invoice value at list price, before trade discounts.

```dax
Gross Sales =
SUM ( 'Fact Sales'[GrossSales] )
```

### Discounts

Trade and promotional discounts.

```dax
Discounts =
SUM ( 'Fact Sales'[DiscountAmount] )
```

### Net Sales

Gross sales less discounts. The headline revenue measure.

```dax
Net Sales =
SUM ( 'Fact Sales'[NetSales] )
```

### COGS

Cost of goods sold at standard cost.

```dax
COGS =
SUM ( 'Fact Sales'[COGS] )
```

### Gross Margin

Net sales less COGS.

```dax
Gross Margin =
[Net Sales] - [COGS]
```

### Gross Margin %

Gross margin as a share of net sales.

```dax
Gross Margin % =
DIVIDE ( [Gross Margin], [Net Sales] )
```

### Units Sold

Units invoiced.

```dax
Units Sold =
SUM ( 'Fact Sales'[Units] )
```

### Discount %

Discounts as a share of gross sales.

```dax
Discount % =
DIVIDE ( [Discounts], [Gross Sales] )
```

### Avg Net Price

Net sales per unit.

```dax
Avg Net Price =
DIVIDE ( [Net Sales], [Units Sold] )
```

### Orders

Number of distinct sales orders.

```dax
Orders =
DISTINCTCOUNT ( 'Fact Sales'[OrderNumber] )
```

### Avg Order Value

Net sales per order.

```dax
Avg Order Value =
DIVIDE ( [Net Sales], [Orders] )
```

### Active Customers

Customers with at least one invoice in context.

```dax
Active Customers =
DISTINCTCOUNT ( 'Fact Sales'[CustomerKey] )
```

### Active SKUs

SKUs with at least one invoice in context.

```dax
Active SKUs =
DISTINCTCOUNT ( 'Fact Sales'[ProductKey] )
```


## 02 Forecast & Budget

### Forecast Net Sales

Latest rolling forecast of net sales (all periods, including future months).

```dax
Forecast Net Sales =
SUM ( 'Fact Forecast'[ForecastNetSales] )
```

### Forecast Units

Latest rolling forecast of units.

```dax
Forecast Units =
SUM ( 'Fact Forecast'[ForecastUnits] )
```

### Forecast COGS

Forecast cost of goods sold.

```dax
Forecast COGS =
SUM ( 'Fact Forecast'[ForecastCOGS] )
```

### Forecast Gross Margin

Forecast net sales less forecast COGS.

```dax
Forecast Gross Margin =
[Forecast Net Sales] - [Forecast COGS]
```

### Forecast Gross Margin %

Forecast gross margin %.

```dax
Forecast Gross Margin % =
DIVIDE ( [Forecast Gross Margin], [Forecast Net Sales] )
```

### Budget Net Sales

Annual operating plan (budget) net sales.

```dax
Budget Net Sales =
SUM ( 'Fact Forecast'[BudgetNetSales] )
```

### Budget Units

Budget units.

```dax
Budget Units =
SUM ( 'Fact Forecast'[BudgetUnits] )
```

### Budget COGS

Budget cost of goods sold.

```dax
Budget COGS =
SUM ( 'Fact Forecast'[BudgetCOGS] )
```

### Budget Gross Margin

Budget net sales less budget COGS.

```dax
Budget Gross Margin =
[Budget Net Sales] - [Budget COGS]
```

### Budget Gross Margin %

Budget gross margin %.

```dax
Budget Gross Margin % =
DIVIDE ( [Budget Gross Margin], [Budget Net Sales] )
```

### Forecast Net Sales (Closed)

Forecast Net Sales restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Forecast Net Sales (Closed) =
CALCULATE ( [Forecast Net Sales], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Forecast Units (Closed)

Forecast Units restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Forecast Units (Closed) =
CALCULATE ( [Forecast Units], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Forecast Gross Margin (Closed)

Forecast Gross Margin restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Forecast Gross Margin (Closed) =
CALCULATE ( [Forecast Gross Margin], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Budget Net Sales (Closed)

Budget Net Sales restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Budget Net Sales (Closed) =
CALCULATE ( [Budget Net Sales], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Budget Units (Closed)

Budget Units restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Budget Units (Closed) =
CALCULATE ( [Budget Units], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Budget Gross Margin (Closed)

Budget Gross Margin restricted to closed periods, so it is like-for-like with actuals (future months are excluded).

```dax
Budget Gross Margin (Closed) =
CALCULATE ( [Budget Gross Margin], KEEPFILTERS ( 'Date'[Is Actual Period] = TRUE () ) )
```

### Budget Gross Margin % (Closed)

Budget GM % for closed periods.

```dax
Budget Gross Margin % (Closed) =
DIVIDE ( [Budget Gross Margin (Closed)], [Budget Net Sales (Closed)] )
```


## 03 Variance

### Var vs Forecast

Actual net sales minus forecast (closed periods). Positive = favourable.

```dax
Var vs Forecast =
VAR _act = [Net Sales]
VAR _fc = [Forecast Net Sales (Closed)]
RETURN
    IF ( NOT ISBLANK ( _act ) || NOT ISBLANK ( _fc ), _act - _fc )
```

### Var % vs Forecast

Variance to forecast as a % of forecast.

```dax
Var % vs Forecast =
DIVIDE ( [Var vs Forecast], [Forecast Net Sales (Closed)] )
```

### Var vs Budget

Actual net sales minus budget (closed periods). Positive = favourable.

```dax
Var vs Budget =
VAR _act = [Net Sales]
VAR _bud = [Budget Net Sales (Closed)]
RETURN
    IF ( NOT ISBLANK ( _act ) || NOT ISBLANK ( _bud ), _act - _bud )
```

### Var % vs Budget

Variance to budget as a % of budget.

```dax
Var % vs Budget =
DIVIDE ( [Var vs Budget], [Budget Net Sales (Closed)] )
```

### Units Var vs Forecast

Units sold minus forecast units.

```dax
Units Var vs Forecast =
IF ( NOT ISBLANK ( [Units Sold] ), [Units Sold] - [Forecast Units (Closed)] )
```

### Units Var % vs Forecast

Unit variance to forecast as a %.

```dax
Units Var % vs Forecast =
DIVIDE ( [Units Var vs Forecast], [Forecast Units (Closed)] )
```

### GM Var vs Budget

Gross margin minus budget gross margin.

```dax
GM Var vs Budget =
IF ( NOT ISBLANK ( [Net Sales] ), [Gross Margin] - [Budget Gross Margin (Closed)] )
```

### GM % pts vs Budget

Gross margin % minus budget GM % (percentage points).

```dax
GM % pts vs Budget =
IF ( NOT ISBLANK ( [Net Sales] ), [Gross Margin %] - [Budget Gross Margin % (Closed)] )
```

### Volume & Mix Effect vs Budget

Part of the budget variance explained by units (SKU x month grain): (actual units - budget units) x budget price. Includes SKU mix.

```dax
Volume & Mix Effect vs Budget =
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
    )
```

### Price & Discount Effect vs Budget

Part of the budget variance explained by realised net price (list price changes and discount depth). Volume + Price = total variance.

```dax
Price & Discount Effect vs Budget =
[Var vs Budget] - [Volume & Mix Effect vs Budget]
```

### Bridge Value

Feeds the Budget -> Actual waterfall. The waterfall total equals actual net sales.

```dax
Bridge Value =
SWITCH (
    SELECTEDVALUE ( 'Variance Bridge'[Step] ),
    "Budget", [Budget Net Sales (Closed)],
    "Volume & Mix", [Volume & Mix Effect vs Budget],
    "Price & Discount", [Price & Discount Effect vs Budget]
)
```


## 04 Forecast Accuracy

### Forecast Accuracy Target

Target forecast accuracy (1 - WMAPE).

```dax
Forecast Accuracy Target =
0.90
```

### Forecast Abs Error

Sum of absolute forecast errors at SKU x Region x Month grain (errors don't cancel out across SKUs).

```dax
Forecast Abs Error =
VAR _grid =
    CROSSJOIN (
        CALCULATETABLE ( VALUES ( 'Date'[Year Month Key] ), 'Date'[Is Actual Period] = TRUE () ),
        VALUES ( 'Product'[ProductKey] ),
        VALUES ( 'Region'[RegionKey] )
    )
RETURN
    SUMX ( _grid, ABS ( [Net Sales] - [Forecast Net Sales] ) )
```

### WMAPE %

Weighted mean absolute percentage error = sum |actual - forecast| / sum actual.

```dax
WMAPE % =
DIVIDE ( [Forecast Abs Error], [Net Sales] )
```

### Forecast Accuracy %

1 - WMAPE, floored at 0. The standard demand-planning accuracy KPI.

```dax
Forecast Accuracy % =
IF ( NOT ISBLANK ( [Net Sales] ), MAX ( 0, 1 - [WMAPE %] ) )
```

### MAPE %

Unweighted mean absolute percentage error across SKU x Month cells (every SKU counts equally).

```dax
MAPE % =
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
    AVERAGEX ( FILTER ( _grid, [@a] > 0 ), ABS ( [@a] - [@f] ) / [@a] )
```

### Forecast Bias %

Positive = over-forecasting, negative = under-forecasting.

```dax
Forecast Bias % =
DIVIDE ( [Forecast Net Sales (Closed)] - [Net Sales], [Net Sales] )
```

### Accuracy vs Target (pts)

Forecast accuracy minus target, in percentage points.

```dax
Accuracy vs Target (pts) =
IF ( NOT ISBLANK ( [Forecast Accuracy %] ), [Forecast Accuracy %] - [Forecast Accuracy Target] )
```


## 05 Reporting Period

### Last Actual Date

Month-end of the latest month with actuals, regardless of filters.

```dax
Last Actual Date =
EOMONTH ( CALCULATE ( MAX ( 'Fact Sales'[OrderDate] ), REMOVEFILTERS () ), 0 )
```

### Reporting Date

The as-of date for every (Month)/(QTD)/(YTD) measure: the end of the selected period, capped at the last closed month. With no date selection it is the last closed month.

```dax
Reporting Date =
VAR _last = [Last Actual Date]
VAR _minCtx = MIN ( 'Date'[Date] )
VAR _maxCtx = MAX ( 'Date'[Date] )
RETURN
    IF ( _minCtx <= _last, MIN ( _maxCtx, _last ) )
```

### Net Sales (Month)

[Net Sales] for the reporting month.

```dax
Net Sales (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Net Sales (Prior Month)

[Net Sales] for the month before the reporting month.

```dax
Net Sales (Prior Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -2 ) + 1, EOMONTH ( _rd, -1 ) ) )
    )
```

### Net Sales (PY Month)

[Net Sales] for the same month last year.

```dax
Net Sales (PY Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -13 ) + 1, EOMONTH ( _rd, -12 ) ) )
    )
```

### Net Sales (QTD)

[Net Sales] for quarter-to-date through the reporting month.

```dax
Net Sales (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Net Sales (Prior QTD)

[Net Sales] for the equivalent quarter-to-date one quarter earlier.

```dax
Net Sales (Prior QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( EOMONTH ( _rd, -3 ) ), QUARTER ( EOMONTH ( _rd, -3 ) ) * 3 - 2, 1 ), EOMONTH ( _rd, -3 ) ) )
    )
```

### Net Sales (PY QTD)

[Net Sales] for the same quarter-to-date last year.

```dax
Net Sales (PY QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, QUARTER ( _rd ) * 3 - 2, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Net Sales (YTD)

[Net Sales] for year-to-date through the reporting month.

```dax
Net Sales (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Net Sales (PY YTD)

[Net Sales] for the same year-to-date period last year.

```dax
Net Sales (PY YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, 1, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Net Sales (R12M)

[Net Sales] for the rolling 12 months ending with the reporting month.

```dax
Net Sales (R12M) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -12 ) + 1, _rd ) )
    )
```

### Net Sales (PY R12M)

[Net Sales] for the rolling 12 months one year earlier.

```dax
Net Sales (PY R12M) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -24 ) + 1, EOMONTH ( _rd, -12 ) ) )
    )
```

### Gross Margin (Month)

[Gross Margin] for the reporting month.

```dax
Gross Margin (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Gross Margin % (Month)

[Gross Margin %] for the reporting month.

```dax
Gross Margin % (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin %], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Gross Margin (PY Month)

[Gross Margin] for the same month last year.

```dax
Gross Margin (PY Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -13 ) + 1, EOMONTH ( _rd, -12 ) ) )
    )
```

### Gross Margin % (PY Month)

[Gross Margin %] for the same month last year.

```dax
Gross Margin % (PY Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin %], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -13 ) + 1, EOMONTH ( _rd, -12 ) ) )
    )
```

### Gross Margin (QTD)

[Gross Margin] for quarter-to-date through the reporting month.

```dax
Gross Margin (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Gross Margin % (QTD)

[Gross Margin %] for quarter-to-date through the reporting month.

```dax
Gross Margin % (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Gross Margin (YTD)

[Gross Margin] for year-to-date through the reporting month.

```dax
Gross Margin (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Gross Margin % (YTD)

[Gross Margin %] for year-to-date through the reporting month.

```dax
Gross Margin % (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Gross Margin (PY YTD)

[Gross Margin] for the same year-to-date period last year.

```dax
Gross Margin (PY YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, 1, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Gross Margin % (PY YTD)

[Gross Margin %] for the same year-to-date period last year.

```dax
Gross Margin % (PY YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Gross Margin %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, 1, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Units Sold (Month)

[Units Sold] for the reporting month.

```dax
Units Sold (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Units Sold], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Discount % (Month)

[Discount %] for the reporting month.

```dax
Discount % (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Discount %], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Units Sold (YTD)

[Units Sold] for year-to-date through the reporting month.

```dax
Units Sold (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Units Sold], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Discount % (YTD)

[Discount %] for year-to-date through the reporting month.

```dax
Discount % (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Discount %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Units Sold (PY YTD)

[Units Sold] for the same year-to-date period last year.

```dax
Units Sold (PY YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Units Sold], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, 1, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Discount % (PY YTD)

[Discount %] for the same year-to-date period last year.

```dax
Discount % (PY YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Discount %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ) - 1, 1, 1 ), EOMONTH ( _rd, -12 ) ) )
    )
```

### Forecast Net Sales (Closed) (Month)

[Forecast Net Sales (Closed)] for the reporting month.

```dax
Forecast Net Sales (Closed) (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Budget Net Sales (Closed) (Month)

[Budget Net Sales (Closed)] for the reporting month.

```dax
Budget Net Sales (Closed) (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Budget Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Var vs Forecast (Month)

[Var vs Forecast] for the reporting month.

```dax
Var vs Forecast (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Forecast], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Var % vs Forecast (Month)

[Var % vs Forecast] for the reporting month.

```dax
Var % vs Forecast (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Forecast], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Var vs Budget (Month)

[Var vs Budget] for the reporting month.

```dax
Var vs Budget (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Budget], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Var % vs Budget (Month)

[Var % vs Budget] for the reporting month.

```dax
Var % vs Budget (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Budget], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Forecast Accuracy % (Month)

[Forecast Accuracy %] for the reporting month.

```dax
Forecast Accuracy % (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Accuracy %], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Forecast Bias % (Month)

[Forecast Bias %] for the reporting month.

```dax
Forecast Bias % (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Bias %], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### GM % pts vs Budget (Month)

[GM % pts vs Budget] for the reporting month.

```dax
GM % pts vs Budget (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [GM % pts vs Budget], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Forecast Net Sales (Closed) (QTD)

[Forecast Net Sales (Closed)] for quarter-to-date through the reporting month.

```dax
Forecast Net Sales (Closed) (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Budget Net Sales (Closed) (QTD)

[Budget Net Sales (Closed)] for quarter-to-date through the reporting month.

```dax
Budget Net Sales (Closed) (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Budget Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Var vs Forecast (QTD)

[Var vs Forecast] for quarter-to-date through the reporting month.

```dax
Var vs Forecast (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Forecast], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Var % vs Forecast (QTD)

[Var % vs Forecast] for quarter-to-date through the reporting month.

```dax
Var % vs Forecast (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Forecast], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Var vs Budget (QTD)

[Var vs Budget] for quarter-to-date through the reporting month.

```dax
Var vs Budget (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Var % vs Budget (QTD)

[Var % vs Budget] for quarter-to-date through the reporting month.

```dax
Var % vs Budget (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Forecast Accuracy % (QTD)

[Forecast Accuracy %] for quarter-to-date through the reporting month.

```dax
Forecast Accuracy % (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Accuracy %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Forecast Bias % (QTD)

[Forecast Bias %] for quarter-to-date through the reporting month.

```dax
Forecast Bias % (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Bias %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### GM % pts vs Budget (QTD)

[GM % pts vs Budget] for quarter-to-date through the reporting month.

```dax
GM % pts vs Budget (QTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [GM % pts vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), QUARTER ( _rd ) * 3 - 2, 1 ), _rd ) )
    )
```

### Forecast Net Sales (Closed) (YTD)

[Forecast Net Sales (Closed)] for year-to-date through the reporting month.

```dax
Forecast Net Sales (Closed) (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Budget Net Sales (Closed) (YTD)

[Budget Net Sales (Closed)] for year-to-date through the reporting month.

```dax
Budget Net Sales (Closed) (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Budget Net Sales (Closed)], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Var vs Forecast (YTD)

[Var vs Forecast] for year-to-date through the reporting month.

```dax
Var vs Forecast (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Forecast], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Var % vs Forecast (YTD)

[Var % vs Forecast] for year-to-date through the reporting month.

```dax
Var % vs Forecast (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Forecast], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Var vs Budget (YTD)

[Var vs Budget] for year-to-date through the reporting month.

```dax
Var vs Budget (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Var % vs Budget (YTD)

[Var % vs Budget] for year-to-date through the reporting month.

```dax
Var % vs Budget (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Var % vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Forecast Accuracy % (YTD)

[Forecast Accuracy %] for year-to-date through the reporting month.

```dax
Forecast Accuracy % (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Accuracy %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Forecast Bias % (YTD)

[Forecast Bias %] for year-to-date through the reporting month.

```dax
Forecast Bias % (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Forecast Bias %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### GM % pts vs Budget (YTD)

[GM % pts vs Budget] for year-to-date through the reporting month.

```dax
GM % pts vs Budget (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [GM % pts vs Budget], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Bridge Value (YTD)

[Bridge Value] for year-to-date through the reporting month.

```dax
Bridge Value (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Bridge Value], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Bridge Value (Month)

[Bridge Value] for the reporting month.

```dax
Bridge Value (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Bridge Value], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Active Customers (Month)

[Active Customers] for the reporting month.

```dax
Active Customers (Month) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Active Customers], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -1 ) + 1, _rd ) )
    )
```

### Active Customers (YTD)

[Active Customers] for year-to-date through the reporting month.

```dax
Active Customers (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Active Customers], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### Avg Order Value (YTD)

[Avg Order Value] for year-to-date through the reporting month.

```dax
Avg Order Value (YTD) =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Avg Order Value], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
    )
```

### MoM %

Month-over-month growth of net sales for the reporting month.

```dax
MoM % =
VAR _cur = [Net Sales (Month)]
VAR _prev = [Net Sales (Prior Month)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### YoY % (Month)

Reporting month vs the same month last year.

```dax
YoY % (Month) =
VAR _cur = [Net Sales (Month)]
VAR _prev = [Net Sales (PY Month)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### QoQ %

Quarter-to-date vs the equivalent period of the prior quarter.

```dax
QoQ % =
VAR _cur = [Net Sales (QTD)]
VAR _prev = [Net Sales (Prior QTD)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### YoY % (QTD)

Quarter-to-date vs the same period last year.

```dax
YoY % (QTD) =
VAR _cur = [Net Sales (QTD)]
VAR _prev = [Net Sales (PY QTD)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### YoY % (YTD)

Year-to-date vs the same period last year.

```dax
YoY % (YTD) =
VAR _cur = [Net Sales (YTD)]
VAR _prev = [Net Sales (PY YTD)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### YoY % (R12M)

Rolling 12 months vs the prior rolling 12 months.

```dax
YoY % (R12M) =
VAR _cur = [Net Sales (R12M)]
VAR _prev = [Net Sales (PY R12M)]
RETURN
    IF ( NOT ISBLANK ( _cur ), DIVIDE ( _cur - _prev, _prev ) )
```

### MoM Change

Month-over-month change in net sales ($).

```dax
MoM Change =
IF ( NOT ISBLANK ( [Net Sales (Month)] ), [Net Sales (Month)] - [Net Sales (Prior Month)] )
```

### YoY Change (YTD)

Year-to-date change vs last year ($).

```dax
YoY Change (YTD) =
IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Net Sales (YTD)] - [Net Sales (PY YTD)] )
```

### GM % pts vs PY (YTD)

Change in YTD gross margin % vs last year (percentage points).

```dax
GM % pts vs PY (YTD) =
IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Gross Margin % (YTD)] - [Gross Margin % (PY YTD)] )
```

### GM % pts vs PY (Month)

Change in the reporting month's gross margin % vs the same month last year.

```dax
GM % pts vs PY (Month) =
IF ( NOT ISBLANK ( [Net Sales (Month)] ), [Gross Margin % (Month)] - [Gross Margin % (PY Month)] )
```

### Discount % pts vs PY (YTD)

Change in YTD discount depth vs last year (percentage points).

```dax
Discount % pts vs PY (YTD) =
IF ( NOT ISBLANK ( [Net Sales (YTD)] ), [Discount % (YTD)] - [Discount % (PY YTD)] )
```


## 06 Time Intelligence (context)

### Net Sales PY

Net sales for the same period last year, for whatever dates are in context.

```dax
Net Sales PY =
CALCULATE ( [Net Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
```

### YoY %

Year-over-year growth for the dates in context.

```dax
YoY % =
IF ( NOT ISBLANK ( [Net Sales] ), DIVIDE ( [Net Sales] - [Net Sales PY], [Net Sales PY] ) )
```

### Net Sales Prior Period

Previous month, quarter or year depending on the level shown in the visual.

```dax
Net Sales Prior Period =
SWITCH (
    TRUE (),
    ISINSCOPE ( 'Date'[Month] ) || ISINSCOPE ( 'Date'[Month Year] ), CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, MONTH ) ),
    ISINSCOPE ( 'Date'[Quarter] ) || ISINSCOPE ( 'Date'[Year Quarter] ), CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, QUARTER ) ),
    CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, YEAR ) )
)
```

### PoP %

Period-over-period growth: MoM at month level, QoQ at quarter level, YoY at year level.

```dax
PoP % =
IF ( NOT ISBLANK ( [Net Sales] ), DIVIDE ( [Net Sales] - [Net Sales Prior Period], [Net Sales Prior Period] ) )
```

### Net Sales Running YTD

Cumulative year-to-date net sales along a date axis (stops at the last closed month).

```dax
Net Sales Running YTD =
IF ( MIN ( 'Date'[Date] ) <= [Last Actual Date], CALCULATE ( [Net Sales], DATESYTD ( 'Date'[Date] ) ) )
```

### Net Sales Running YTD PY

Prior-year cumulative YTD along a date axis.

```dax
Net Sales Running YTD PY =
CALCULATE ( CALCULATE ( [Net Sales], DATESYTD ( 'Date'[Date] ) ), SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
```

### Budget Running YTD

Cumulative budget along a date axis (full year).

```dax
Budget Running YTD =
CALCULATE ( [Budget Net Sales], DATESYTD ( 'Date'[Date] ) )
```

### Forecast Running YTD

Cumulative forecast along a date axis (full year).

```dax
Forecast Running YTD =
CALCULATE ( [Forecast Net Sales], DATESYTD ( 'Date'[Date] ) )
```

### Net Sales 3M Avg

Three-month moving average of net sales.

```dax
Net Sales 3M Avg =
VAR _end = MAX ( 'Date'[Date] )
RETURN
    IF (
        MIN ( 'Date'[Date] ) <= [Last Actual Date],
        CALCULATE ( [Net Sales], DATESINPERIOD ( 'Date'[Date], _end, -3, MONTH ) ) / 3
    )
```


## 07 Outlook & KPIs

### Full Year Outlook

Latest estimate for the year: YTD actuals plus forecast for the remaining months.

```dax
Full Year Outlook =
VAR _rd = [Reporting Date]
VAR _ytd = CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), _rd ) )
VAR _rest = CALCULATE ( [Forecast Net Sales], DATESBETWEEN ( 'Date'[Date], _rd + 1, DATE ( YEAR ( _rd ), 12, 31 ) ) )
RETURN
    IF ( NOT ISBLANK ( _rd ), _ytd + _rest )
```

### Full Year Budget

Full-year budget for the reporting year.

```dax
Full Year Budget =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Budget Net Sales], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( _rd ), 1, 1 ), DATE ( YEAR ( _rd ), 12, 31 ) ) )
    )
```

### Outlook vs Budget

Full-year outlook minus full-year budget.

```dax
Outlook vs Budget =
[Full Year Outlook] - [Full Year Budget]
```

### Outlook vs Budget %

Full-year outlook vs budget, %.

```dax
Outlook vs Budget % =
DIVIDE ( [Outlook vs Budget], [Full Year Budget] )
```

### Budget Attainment % (YTD)

YTD actuals as a % of YTD budget.

```dax
Budget Attainment % (YTD) =
DIVIDE ( [Net Sales (YTD)], [Budget Net Sales (Closed) (YTD)] )
```

### Full Year Budget Achieved %

Share of the full-year budget already delivered.

```dax
Full Year Budget Achieved % =
DIVIDE ( [Net Sales (YTD)], [Full Year Budget] )
```

### Annualised Run Rate

Last three closed months x 4.

```dax
Annualised Run Rate =
VAR _rd = [Reporting Date]
RETURN
    IF (
        NOT ISBLANK ( _rd ),
        CALCULATE ( [Net Sales], DATESBETWEEN ( 'Date'[Date], EOMONTH ( _rd, -3 ) + 1, _rd ) ) * 4
    )
```

### Revenue per Customer (YTD)

YTD net sales per active customer.

```dax
Revenue per Customer (YTD) =
DIVIDE ( [Net Sales (YTD)], [Active Customers (YTD)] )
```


## 08 Ranking & Mix

### Product Rank (YTD)

Rank of the product by YTD net sales within the current selection.

```dax
Product Rank (YTD) =
IF ( ISINSCOPE ( 'Product'[Product] ), RANKX ( ALLSELECTED ( 'Product'[Product] ), [Net Sales (YTD)], , DESC, DENSE ) )
```

### Customer Rank (YTD)

Rank of the customer by YTD net sales within the current selection.

```dax
Customer Rank (YTD) =
IF ( ISINSCOPE ( 'Customer'[Customer] ), RANKX ( ALLSELECTED ( 'Customer'[Customer] ), [Net Sales (YTD)], , DESC, DENSE ) )
```

### Share of Net Sales (YTD)

Product/brand/category share of YTD net sales within the current selection.

```dax
Share of Net Sales (YTD) =
DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Product' ) ) )
```

### Channel Share (YTD)

Channel share of YTD net sales.

```dax
Channel Share (YTD) =
DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Channel' ) ) )
```

### Region Share (YTD)

Region share of YTD net sales.

```dax
Region Share (YTD) =
DIVIDE ( [Net Sales (YTD)], CALCULATE ( [Net Sales (YTD)], ALLSELECTED ( 'Region' ) ) )
```


## 09 Labels & Formatting

### Report Title

Static report title.

```dax
Report Title =
"Month-End Financial Report"
```

### Reporting Period Label

Dynamic subtitle showing the period being reported.

```dax
Reporting Period Label =
"Close period  ·  " & FORMAT ( [Reporting Date], "MMMM yyyy" )
```

### Data As Of Label

Footer label with the actuals cut-off.

```dax
Data As Of Label =
"Actuals through " & FORMAT ( [Last Actual Date], "d MMM yyyy" ) & "  ·  USD"
```

### KPI Label Net Sales (Month)

Subtitle for the monthly net sales KPI tile.

```dax
KPI Label Net Sales (Month) =
VAR _vf = [Var % vs Forecast (Month)]
VAR _yoy = [YoY % (Month)]
RETURN
    IF ( NOT ISBLANK ( _vf ), IF ( _vf >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _vf ), "0.0%" ) & " vs Fcst    " & IF ( _yoy >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _yoy ), "0.0%" ) & " YoY" )
```

### KPI Label Gross Margin % (Month)

Subtitle for the gross margin % KPI tile.

```dax
KPI Label Gross Margin % (Month) =
VAR _vb = [GM % pts vs Budget (Month)]
VAR _py = [GM % pts vs PY (Month)]
RETURN
    IF ( NOT ISBLANK ( _vb ), IF ( _vb * 100 >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _vb * 100 ), "0.0" ) & " pp vs Bud    " & IF ( _py * 100 >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _py * 100 ), "0.0" ) & " pp YoY" )
```

### KPI Label Net Sales (YTD)

Subtitle for the YTD net sales KPI tile.

```dax
KPI Label Net Sales (YTD) =
VAR _yoy = [YoY % (YTD)]
VAR _att = [Budget Attainment % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _yoy ), IF ( _yoy >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _yoy ), "0.0%" ) & " YoY    " & FORMAT ( _att, "0.0%" ) & " of budget" )
```

### KPI Label Outlook

Subtitle for the full-year outlook KPI tile.

```dax
KPI Label Outlook =
VAR _v = [Outlook vs Budget %]
RETURN
    IF ( NOT ISBLANK ( _v ), IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%" ) & " vs FY budget  (" & FORMAT ( [Full Year Budget], "$#,0.0,,") & "M)" )
```

### KPI Label Accuracy (Month)

Subtitle for the forecast accuracy KPI tile.

```dax
KPI Label Accuracy (Month) =
VAR _a = [Forecast Accuracy % (Month)]
VAR _b = [Forecast Bias % (Month)]
RETURN
    IF ( NOT ISBLANK ( _a ), "Target " & FORMAT ( [Forecast Accuracy Target], "0%" ) & "    Bias " & FORMAT ( _b, "+0.0%;-0.0%" ) )
```

### KPI Label Var vs Forecast (Month)

Subtitle for the monthly forecast variance tile.

```dax
KPI Label Var vs Forecast (Month) =
VAR _v = [Var % vs Forecast (Month)]
RETURN
    IF ( NOT ISBLANK ( _v ), IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%" ) & " of forecast  ·  " & FORMAT ( [Forecast Net Sales (Closed) (Month)], "$#,0.00,,") & "M fcst" )
```

### KPI Label Var vs Budget (YTD)

Subtitle for the YTD budget variance tile.

```dax
KPI Label Var vs Budget (YTD) =
VAR _v = [Var % vs Budget (YTD)]
RETURN
    IF ( NOT ISBLANK ( _v ), IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%" ) & " of budget  ·  " & FORMAT ( [Budget Net Sales (Closed) (YTD)], "$#,0.0,,") & "M bud" )
```

### KPI Label Accuracy (YTD)

Subtitle for the YTD forecast accuracy tile.

```dax
KPI Label Accuracy (YTD) =
VAR _a = [Forecast Accuracy % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _a ), "MAPE (SKU) " & FORMAT ( CALCULATE ( [MAPE %], DATESBETWEEN ( 'Date'[Date], DATE ( YEAR ( [Reporting Date] ), 1, 1 ), [Reporting Date] ) ), "0.0%" ) & "    Target " & FORMAT ( [Forecast Accuracy Target], "0%" ) )
```

### KPI Label Bias (YTD)

Subtitle for the forecast bias tile.

```dax
KPI Label Bias (YTD) =
VAR _b = [Forecast Bias % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _b ), IF ( _b > 0.005, "Over-forecasting", IF ( _b < -0.005, "Under-forecasting", "Unbiased" ) ) & "  ·  ±0.5% tolerance" )
```

### KPI Label QTD

Subtitle for the QTD tile.

```dax
KPI Label QTD =
VAR _q = [QoQ %]
VAR _y = [YoY % (QTD)]
RETURN
    IF ( NOT ISBLANK ( _q ), IF ( _q >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _q ), "0.0%" ) & " QoQ    " & IF ( _y >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _y ), "0.0%" ) & " YoY" )
```

### KPI Label YTD YoY

Subtitle for the YTD vs PY tile.

```dax
KPI Label YTD YoY =
VAR _y = [YoY % (YTD)]
RETURN
    IF ( NOT ISBLANK ( _y ), IF ( _y >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _y ), "0.0%" ) & " vs PY  (" & FORMAT ( [YoY Change (YTD)], "+$#,0.0,,;-$#,0.0,,") & "M)" )
```

### KPI Label R12M

Subtitle for the rolling 12M tile.

```dax
KPI Label R12M =
VAR _y = [YoY % (R12M)]
RETURN
    IF ( NOT ISBLANK ( _y ), IF ( _y >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _y ), "0.0%" ) & " vs prior 12M  ·  run rate " & FORMAT ( [Annualised Run Rate], "$#,0.0,,") & "M" )
```

### KPI Label GM % (YTD)

Subtitle for the YTD gross margin % tile.

```dax
KPI Label GM % (YTD) =
VAR _p = [GM % pts vs PY (YTD)]
RETURN
    IF ( NOT ISBLANK ( _p ), IF ( _p * 100 >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _p * 100 ), "0.0" ) & " pp vs PY  ·  GM " & FORMAT ( [Gross Margin (YTD)], "$#,0.0,,") & "M" )
```

### KPI Label Discount % (YTD)

Subtitle for the YTD discount % tile.

```dax
KPI Label Discount % (YTD) =
VAR _p = [Discount % pts vs PY (YTD)]
RETURN
    IF ( NOT ISBLANK ( _p ), IF ( _p * 100 >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _p * 100 ), "0.0" ) & " pp vs PY  ·  " & FORMAT ( [Discounts], "$#,0.0,,") & "M all-time" )
```

### Color Var % vs Forecast

Hex colour for conditional formatting driven by [Var % vs Forecast]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Forecast =
VAR _v = [Var % vs Forecast]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Var % vs Budget

Hex colour for conditional formatting driven by [Var % vs Budget]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Budget =
VAR _v = [Var % vs Budget]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Var % vs Forecast (Month)

Hex colour for conditional formatting driven by [Var % vs Forecast (Month)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Forecast (Month) =
VAR _v = [Var % vs Forecast (Month)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Var % vs Budget (YTD)

Hex colour for conditional formatting driven by [Var % vs Budget (YTD)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Budget (YTD) =
VAR _v = [Var % vs Budget (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color YoY % (Month)

Hex colour for conditional formatting driven by [YoY % (Month)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color YoY % (Month) =
VAR _v = [YoY % (Month)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color YoY % (YTD)

Hex colour for conditional formatting driven by [YoY % (YTD)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color YoY % (YTD) =
VAR _v = [YoY % (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color YoY %

Hex colour for conditional formatting driven by [YoY %]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color YoY % =
VAR _v = [YoY %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color PoP %

Hex colour for conditional formatting driven by [PoP %]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color PoP % =
VAR _v = [PoP %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color GM pts vs Budget (Month)

Hex colour for conditional formatting driven by [GM % pts vs Budget (Month)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color GM pts vs Budget (Month) =
VAR _v = [GM % pts vs Budget (Month)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color GM pts vs PY (YTD)

Hex colour for conditional formatting driven by [GM % pts vs PY (YTD)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color GM pts vs PY (YTD) =
VAR _v = [GM % pts vs PY (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Discount pts vs PY (YTD)

Hex colour for discount depth change: deeper discounts (positive) are unfavourable.

```dax
Color Discount pts vs PY (YTD) =
VAR _v = [Discount % pts vs PY (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#D03B3B",
        _v <= -0.005, "#006300",
        "#52514E"
    )
```

### Color Outlook vs Budget

Hex colour for conditional formatting driven by [Outlook vs Budget %]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Outlook vs Budget =
VAR _v = [Outlook vs Budget %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color QoQ %

Hex colour for conditional formatting driven by [QoQ %]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color QoQ % =
VAR _v = [QoQ %]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color YoY % (R12M)

Hex colour for conditional formatting driven by [YoY % (R12M)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color YoY % (R12M) =
VAR _v = [YoY % (R12M)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```


## 04 Forecast Accuracy

### Accuracy vs Target (Month)

Reporting-month forecast accuracy minus target.

```dax
Accuracy vs Target (Month) =
IF ( NOT ISBLANK ( [Forecast Accuracy % (Month)] ), [Forecast Accuracy % (Month)] - [Forecast Accuracy Target] )
```

### Accuracy vs Target (YTD)

YTD forecast accuracy minus target.

```dax
Accuracy vs Target (YTD) =
IF ( NOT ISBLANK ( [Forecast Accuracy % (YTD)] ), [Forecast Accuracy % (YTD)] - [Forecast Accuracy Target] )
```


## 09 Labels & Formatting

### Color Accuracy vs Target (YTD)

Hex colour for conditional formatting driven by [Accuracy vs Target (YTD)]: green favourable, red unfavourable, grey within ±0.0%.

```dax
Color Accuracy vs Target (YTD) =
VAR _v = [Accuracy vs Target (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.0001, "#006300",
        _v <= -0.0001, "#D03B3B",
        "#52514E"
    )
```

### Color Accuracy vs Target (Month)

Hex colour for conditional formatting driven by [Accuracy vs Target (Month)]: green favourable, red unfavourable, grey within ±0.0%.

```dax
Color Accuracy vs Target (Month) =
VAR _v = [Accuracy vs Target (Month)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.0001, "#006300",
        _v <= -0.0001, "#D03B3B",
        "#52514E"
    )
```

### Color Var % vs Budget (Month)

Hex colour for conditional formatting driven by [Var % vs Budget (Month)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Budget (Month) =
VAR _v = [Var % vs Budget (Month)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Var % vs Forecast (YTD)

Hex colour for conditional formatting driven by [Var % vs Forecast (YTD)]: green favourable, red unfavourable, grey within ±0.5%.

```dax
Color Var % vs Forecast (YTD) =
VAR _v = [Var % vs Forecast (YTD)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _v ), "#898781",
        _v >= 0.005, "#006300",
        _v <= -0.005, "#D03B3B",
        "#52514E"
    )
```

### Color Bias (YTD)

Green when forecast bias is within ±0.5%.

```dax
Color Bias (YTD) =
VAR _b = [Forecast Bias % (YTD)]
RETURN
    IF ( ABS ( _b ) <= 0.005, "#006300", "#52514E" )
```

### Fill Var vs Forecast

Bar fill colour for forecast variance: green favourable, red unfavourable.

```dax
Fill Var vs Forecast =
VAR _v = [Var vs Forecast]
RETURN
    IF ( ISBLANK ( _v ), BLANK (), IF ( _v >= 0, "#0CA30C", "#D03B3B" ) )
```

### Fill Var vs Forecast (Month)

Bar fill colour for the reporting month's forecast variance.

```dax
Fill Var vs Forecast (Month) =
VAR _v = [Var vs Forecast (Month)]
RETURN
    IF ( ISBLANK ( _v ), BLANK (), IF ( _v >= 0, "#0CA30C", "#D03B3B" ) )
```

### Fill Accuracy

Column fill for forecast accuracy: blue at/above target, orange below.

```dax
Fill Accuracy =
VAR _a = [Forecast Accuracy %]
RETURN
    IF ( ISBLANK ( _a ), BLANK (), IF ( _a >= [Forecast Accuracy Target], "#2A78D6", "#EB6834" ) )
```
