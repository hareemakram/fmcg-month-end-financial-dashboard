"""Aggregates the CSVs into a compact JSON cube that powers preview/dashboard-preview.html."""
import json
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(ROOT, "data")
s = pd.read_csv(os.path.join(D, "fact_sales.csv"))
f = pd.read_csv(os.path.join(D, "fact_forecast.csv"))
prod = pd.read_csv(os.path.join(D, "dim_product.csv"))
cust = pd.read_csv(os.path.join(D, "dim_customer.csv"))
reg = pd.read_csv(os.path.join(D, "dim_region.csv"))
ch = pd.read_csv(os.path.join(D, "dim_channel.csv"))

months = pd.date_range("2024-01-01", "2026-12-01", freq="MS").strftime("%Y-%m").tolist()
mi = {m: i for i, m in enumerate(months)}
s["m"] = s.OrderDate.str[:7].map(mi)
f["m"] = f.MonthStartDate.str[:7].map(mi)

a = s.groupby(["m", "ProductKey", "RegionKey", "ChannelKey"], as_index=False)[["Units", "GrossSales", "DiscountAmount", "NetSales", "COGS"]].sum()
fc = f.groupby(["m", "ProductKey", "RegionKey", "ChannelKey"], as_index=False)[["ForecastUnits", "ForecastNetSales", "ForecastCOGS", "BudgetUnits", "BudgetNetSales", "BudgetCOGS"]].sum()
s2 = s.merge(prod[["ProductKey", "Category"]])
cats = sorted(prod.Category.unique())
s2["c"] = s2.Category.map({c: i for i, c in enumerate(cats)})
cu = s2.groupby(["m", "CustomerKey", "c"], as_index=False)[["NetSales", "COGS"]].sum()


def cols(df, spec):
    return {k: (df[c].round(d).tolist() if d else df[c].astype(int).tolist()) for k, (c, d) in spec.items()}


out = {
    "months": months,
    "lastClosed": int(s.m.max()),
    "categories": cats,
    "regions": reg.Region.tolist(),
    "channels": ch.Channel.tolist(),
    "products": [{"name": r.ProductName, "brand": r.Brand, "cat": cats.index(r.Category)} for r in prod.itertuples()],
    "customers": [{"name": r.CustomerName, "region": int(r.RegionKey) - 1, "channel": int(r.ChannelKey) - 1} for r in cust.itertuples()],
    "act": cols(a, {"m": ("m", 0), "p": ("ProductKey", 0), "r": ("RegionKey", 0), "c": ("ChannelKey", 0), "u": ("Units", 0),
                    "g": ("GrossSales", 0), "d": ("DiscountAmount", 0), "n": ("NetSales", 0), "k": ("COGS", 0)}),
    "plan": cols(fc, {"m": ("m", 0), "p": ("ProductKey", 0), "r": ("RegionKey", 0), "c": ("ChannelKey", 0),
                      "fu": ("ForecastUnits", 0), "fn": ("ForecastNetSales", 0), "fk": ("ForecastCOGS", 0),
                      "bu": ("BudgetUnits", 0), "bn": ("BudgetNetSales", 0), "bk": ("BudgetCOGS", 0)}),
    "cust": cols(cu, {"m": ("m", 0), "k": ("CustomerKey", 0), "c": ("c", 0), "n": ("NetSales", 0), "g": ("COGS", 0)}),
}
# keys -> 0-based indexes
for t in ("act", "plan"):
    out[t]["p"] = [x - 1 for x in out[t]["p"]]
    out[t]["r"] = [x - 1 for x in out[t]["r"]]
    out[t]["c"] = [x - 1 for x in out[t]["c"]]
out["cust"]["k"] = [x - 1 for x in out["cust"]["k"]]
js = json.dumps(out, separators=(",", ":"))
path = os.path.join(ROOT, "preview", "preview-data.json")
open(path, "w").write(js)
print(f"{len(js)/1e6:.2f} MB  act={len(a)} plan={len(fc)} cust={len(cu)}")

tpl = open(os.path.join(ROOT, "scripts", "preview_template.html"), encoding="utf-8").read()
html = tpl.replace("/*__DATA__*/null", js)
open(os.path.join(ROOT, "preview", "dashboard-preview.html"), "w", encoding="utf-8").write(html)
os.remove(path)
print("wrote preview/dashboard-preview.html")
