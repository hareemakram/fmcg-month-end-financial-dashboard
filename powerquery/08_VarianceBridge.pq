// Query: Variance Bridge
let
    // Disconnected helper table that drives the Budget -> Actual waterfall
    Source = #table(
        type table [Step = text, #"Step Order" = Int64.Type],
        {{"Budget", 1}, {"Volume & Mix", 2}, {"Price & Discount", 3}})
in
    Source
