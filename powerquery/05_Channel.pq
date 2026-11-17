// Query: Channel
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_channel.csv"), [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
        {"ChannelKey", Int64.Type}, {"Channel", type text}, {"ChannelGroup", type text}}, "en-US"),
    Renamed = Table.RenameColumns(ChangedType, {{"ChannelGroup", "Channel Group"}})
in
    Renamed
