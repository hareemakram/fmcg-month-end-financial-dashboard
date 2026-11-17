// Query: Region
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_region.csv"), [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"RegionKey", Int64.Type}, {"Region", type text}, {"RegionalDirector", type text}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {{"RegionalDirector", "Regional Director"}})
in
    Renamed
