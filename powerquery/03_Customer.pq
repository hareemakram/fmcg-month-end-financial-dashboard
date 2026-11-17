// Query: Customer
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_customer.csv"), [Delimiter = ",", Columns = 8, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"CustomerKey", Int64.Type}, {"CustomerCode", type text}, {"CustomerName", type text}, {"City", type text},
        {"RegionKey", Int64.Type}, {"ChannelKey", Int64.Type}, {"CustomerTier", type text}, {"CustomerSince", type date}}, "en-US"),
    // Region and channel are conformed dimensions joined to the facts directly (no snowflake)
    RemovedKeys = Table.RemoveColumns(ChangedType, {"RegionKey", "ChannelKey"}),
    Renamed = Table.RenameColumns(RemovedKeys, {
        {"CustomerCode", "Customer Code"}, {"CustomerName", "Customer"}, {"CustomerTier", "Customer Tier"}, {"CustomerSince", "Customer Since"}}),
    AddTierOrder = Table.AddColumn(Renamed, "Tier Order", each
        if [Customer Tier] = "Key Account" then 1 else if [Customer Tier] = "Gold" then 2
        else if [Customer Tier] = "Silver" then 3 else 4, Int64.Type)
in
    AddTierOrder
