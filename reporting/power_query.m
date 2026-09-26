// Power Query (M) — Knapsack 0/1 benchmark results
//
// Usage: Power BI Desktop > Get Data > Blank Query > Advanced Editor > paste this,
// then set FilePath below to the local path of benchmark_results.csv.
//
// Produces one clean table (BenchmarkResults) ready for visuals: time vs n by
// algorithm, quality vs n, gap-to-optimum by correlation type, etc.

let
    FilePath = "C:\Path\To\benchmarking_knapsack01\benchmark_results.csv",

    Source = Csv.Document(
        File.Contents(FilePath),
        [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    Typed = Table.TransformColumnTypes(PromotedHeaders, {
        {"correlation", type text},
        {"n", Int64.Type},
        {"capacity_type", type text},
        {"capacity_value", Int64.Type},
        {"algorithm", type text},
        {"value", type number},
        {"time_ms", type number},
        {"usage_percent", type number},
        {"items_selected", Int64.Type}
    }),

    // Family grouping, used to color/filter by algorithm class in the report
    AddFamily = Table.AddColumn(Typed, "family", each
        if List.Contains({"Brute Force", "Dynamic Programming", "DP Top-Down", "Branch and Bound"}, [algorithm]) then "Exact"
        else if List.Contains({"Greedy Ratio", "Greedy Value", "Greedy Weight", "Fractional Knapsack"}, [algorithm]) then "Greedy"
        else if List.Contains({"FPTAS (ε=0.1)", "FPTAS (ε=0.05)", "FPTAS Adaptive"}, [algorithm]) then "Approximation"
        else "Metaheuristic",
        type text
    ),

    // Relative quality: value / best value found for the same instance size n
    // (a proxy for "% of the best known solution at this size" when the true optimum isn't tagged per-row)
    GroupedMax = Table.Group(AddFamily, {"n"}, {{"max_value", each List.Max([value]), type number}}),
    Merged = Table.NestedJoin(AddFamily, {"n"}, GroupedMax, {"n"}, "MaxTable", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "MaxTable", {"max_value"}),
    AddRelQuality = Table.AddColumn(Expanded, "relative_quality_pct", each
        if [max_value] = 0 then null else [value] / [max_value] * 100,
        type number
    ),

    Final = Table.RemoveColumns(AddRelQuality, {"max_value"})
in
    Final
