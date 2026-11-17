# Data dictionary

## Relationships

All are one-to-many with single-direction filtering from the dimension to the fact.

| From (many) | To (one) |
|---|---|
| `Fact Sales[OrderDate]` | `Date[Date]` |
| `Fact Sales[ProductKey]` | `Product[ProductKey]` |
| `Fact Sales[CustomerKey]` | `Customer[CustomerKey]` |
| `Fact Sales[RegionKey]` | `Region[RegionKey]` |
| `Fact Sales[ChannelKey]` | `Channel[ChannelKey]` |
| `Fact Forecast[MonthStartDate]` | `Date[Date]` |
| `Fact Forecast[ProductKey]` | `Product[ProductKey]` |
| `Fact Forecast[RegionKey]` | `Region[RegionKey]` |
| `Fact Forecast[ChannelKey]` | `Channel[ChannelKey]` |

## Date

One row per day, 1 Jan 2024 – 31 Dec 2026 (generated in Power Query)

| Column | Type | Notes |
|---|---|---|
| Date | dateTime | date table key |
| Year | int64 |  |
| Quarter No | int64 | hidden |
| Quarter | string | sorted by Quarter No |
| Year Quarter | string | sorted by Year Quarter Key |
| Year Quarter Key | int64 | hidden |
| Month No | int64 | hidden |
| Month | string | sorted by Month No |
| Month Name | string | sorted by Month No |
| Month Year | string | sorted by Year Month Key |
| Year Month Key | int64 | hidden |
| Month Start | dateTime |  |
| Month End | dateTime |  |
| Half | string |  |
| Day | int64 |  |
| Weekday No | int64 | hidden |
| Weekday | string | sorted by Weekday No |
| Week of Year | int64 |  |
| Is Weekend | boolean |  |
| Is Actual Period | boolean (calculated) | TRUE for every date up to the end of the latest month that has actuals (the last closed month). |
| Month Offset | int64 (calculated) | 0 = last closed month, -1 = the month before, +1 = first forecast-only month. Drives the rolling-window visual filters. |
| Year Offset | int64 (calculated) | 0 = the year of the last closed month, -1 = prior year. |

**Is Actual Period**

```dax
Is Actual Period =
'Date'[Date] <= EOMONTH ( MAX ( 'Fact Sales'[OrderDate] ), 0 )
```

**Month Offset**

```dax
Month Offset =
VAR _last = EOMONTH ( MAX ( 'Fact Sales'[OrderDate] ), 0 )
RETURN
    ( 'Date'[Year] * 12 + 'Date'[Month No] ) - ( YEAR ( _last ) * 12 + MONTH ( _last ) )
```

**Year Offset**

```dax
Year Offset =
'Date'[Year] - YEAR ( MAX ( 'Fact Sales'[OrderDate] ) )
```

Hierarchy **Calendar**: Year › Quarter › Month › Date

## Product

One row per SKU (46)

| Column | Type | Notes |
|---|---|---|
| ProductKey | int64 | hidden |
| SKU | string |  |
| Product | string |  |
| Brand | string |  |
| Category | string |  |
| Segment | string |  |
| Pack Type | string |  |
| List Price | double |  |
| Standard Cost | double |  |
| Launch Date | dateTime |  |
| Price Band | string |  |
| Standard Margin % | double |  |

Hierarchy **Product Hierarchy**: Category › Brand › Product

## Customer

One row per customer (78)

| Column | Type | Notes |
|---|---|---|
| CustomerKey | int64 | hidden |
| Customer Code | string |  |
| Customer | string |  |
| City | string |  |
| Customer Tier | string | sorted by Tier Order |
| Customer Since | dateTime |  |
| Tier Order | int64 | hidden |

## Region

One row per sales region (6)

| Column | Type | Notes |
|---|---|---|
| RegionKey | int64 | hidden |
| Region | string |  |
| Regional Director | string |  |

## Channel

One row per channel (5)

| Column | Type | Notes |
|---|---|---|
| ChannelKey | int64 | hidden |
| Channel | string |  |
| Channel Group | string |  |

## Fact Sales

One row per sales order line (174,800), Jan 2024 – Oct 2026

| Column | Type | Notes |
|---|---|---|
| SalesLineID | int64 | hidden |
| OrderNumber | string | hidden |
| OrderDate | dateTime | hidden |
| ProductKey | int64 | hidden |
| CustomerKey | int64 | hidden |
| RegionKey | int64 | hidden |
| ChannelKey | int64 | hidden |
| Units | int64 | hidden |
| UnitListPrice | double | hidden |
| GrossSales | double | hidden |
| DiscountAmount | double | hidden |
| NetSales | double | hidden |
| COGS | double | hidden |

## Fact Forecast

Month × SKU × region × channel (45,618 rows), Jan 2024 – Dec 2026, latest rolling forecast and budget side by side

| Column | Type | Notes |
|---|---|---|
| ForecastLineID | int64 | hidden |
| MonthStartDate | dateTime | hidden |
| ForecastVersion | string | hidden |
| ProductKey | int64 | hidden |
| RegionKey | int64 | hidden |
| ChannelKey | int64 | hidden |
| ForecastUnits | int64 | hidden |
| ForecastNetSales | double | hidden |
| ForecastCOGS | double | hidden |
| BudgetUnits | int64 | hidden |
| BudgetNetSales | double | hidden |
| BudgetCOGS | double | hidden |

## Variance Bridge

3 rows: Budget, Volume & Mix, Price & Discount (disconnected helper for the waterfall)

| Column | Type | Notes |
|---|---|---|
| Step | string | sorted by Step Order |
| Step Order | int64 | hidden |

## _Measures

Empty table that holds the 182 measures

| Column | Type | Notes |
|---|---|---|
| MeasureHelper | string | hidden |
