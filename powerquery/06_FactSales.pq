// Query: Fact Sales
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_sales.csv"), [Delimiter = ",", Columns = 14, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"SalesLineID", Int64.Type}, {"OrderNumber", type text}, {"OrderDate", type date},
        {"ProductKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"RegionKey", Int64.Type}, {"ChannelKey", Int64.Type},
        {"Units", Int64.Type}, {"UnitListPrice", type number}, {"GrossSales", type number},
        {"DiscountAmount", type number}, {"NetSales", type number}, {"COGS", type number}}, "en-US"),
    // Guard rails: drop malformed rows rather than failing the whole refresh
    RemovedErrors = Table.RemoveRowsWithErrors(ChangedType, {"OrderDate", "ProductKey", "NetSales"}),
    FilteredValid = Table.SelectRows(RemovedErrors, each [OrderDate] <> null and [Units] <> null)
in
    FilteredValid
