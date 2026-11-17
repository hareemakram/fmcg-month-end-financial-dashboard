// Query: Date
let
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
    AddIsWeekend
