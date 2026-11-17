// Query: Product
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_product.csv"), [Delimiter = ",", Columns = 10, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"ProductKey", Int64.Type}, {"SKU", type text}, {"ProductName", type text}, {"Brand", type text},
        {"Category", type text}, {"Segment", type text}, {"PackType", type text},
        {"UnitListPrice", type number}, {"UnitCost", type number}, {"LaunchDate", type date}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {
        {"ProductName", "Product"}, {"PackType", "Pack Type"}, {"UnitListPrice", "List Price"},
        {"UnitCost", "Standard Cost"}, {"LaunchDate", "Launch Date"}}),
    AddPriceBand = Table.AddColumn(Renamed, "Price Band", each
        if [List Price] < 2 then "Under $2"
        else if [List Price] < 5 then "$2 - $5"
        else if [List Price] < 10 then "$5 - $10"
        else "$10+", type text),
    AddStdMargin = Table.AddColumn(AddPriceBand, "Standard Margin %", each 1 - [Standard Cost] / [List Price], Percentage.Type)
in
    AddStdMargin
