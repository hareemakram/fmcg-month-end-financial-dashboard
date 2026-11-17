// Query: Fact Forecast
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_forecast.csv"), [Delimiter = ",", Columns = 13, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"ForecastLineID", Int64.Type}, {"MonthStartDate", type date}, {"ForecastVersion", type text},
        {"ProductKey", Int64.Type}, {"RegionKey", Int64.Type}, {"ChannelKey", Int64.Type},
        {"ForecastUnits", Int64.Type}, {"ForecastNetSales", type number}, {"ForecastCOGS", type number},
        {"BudgetUnits", Int64.Type}, {"BudgetNetSales", type number}, {"BudgetCOGS", type number}}, "en-US"),
    RemovedErrors = Table.RemoveRowsWithErrors(ChangedType, {"MonthStartDate", "ProductKey"})
in
    RemovedErrors
