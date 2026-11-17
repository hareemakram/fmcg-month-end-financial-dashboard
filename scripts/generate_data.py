"""
Synthetic FMCG dataset generator for the Month-End Financial Reporting dashboard.

Company: "Aurora Consumer Goods" (fictional). Currency: USD.
Actuals:  2024-01-01 .. 2026-10-31  (October 2026 is the latest closed month)
Forecast: 2024-01 .. 2026-12  (latest rolling forecast, month x SKU x region x channel)
Budget:   2024-01 .. 2026-12  (annual operating plan, same grain)

Run:  python generate_data.py  [output_dir]
Deterministic (fixed seed), so the numbers in the preview match the model.
"""
import re
import sys
import os
import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

ACTUALS_END = pd.Timestamp("2026-10-31")
months = pd.date_range("2024-01-01", "2026-12-01", freq="MS")

# --------------------------------------------------------------------------------------
# Dimensions
# --------------------------------------------------------------------------------------
categories = {
    #  category        cogs%  season (Jan..Dec)                                         growth
    "Beverages":      (0.52, [0.80, 0.82, 0.92, 1.00, 1.12, 1.25, 1.32, 1.28, 1.08, 0.95, 0.85, 1.02], 0.07),
    "Snacks":         (0.48, [0.92, 0.90, 0.96, 1.00, 1.02, 1.05, 1.06, 1.04, 1.00, 1.00, 1.00, 1.12], 0.06),
    "Dairy":          (0.62, [1.00, 0.98, 1.00, 1.00, 1.02, 1.00, 0.98, 0.98, 1.00, 1.01, 1.00, 1.04], 0.03),
    "Personal Care":  (0.42, [0.95, 0.93, 0.98, 1.00, 1.02, 1.03, 1.02, 1.00, 0.98, 1.00, 1.05, 1.12], 0.09),
    "Home Care":      (0.50, [1.00, 0.97, 1.05, 1.06, 1.02, 0.98, 0.96, 0.97, 1.00, 1.00, 1.00, 1.00], 0.04),
    "Confectionery":  (0.45, [0.90, 1.18, 0.95, 1.05, 0.92, 0.90, 0.88, 0.90, 0.95, 1.10, 1.08, 1.40], 0.05),
}
brands = {
    "Beverages": {"FreshSpring": [("Still Water 500ml", 0.65), ("Still Water 1.5L", 1.10), ("Sparkling Water 750ml", 1.25), ("Still Water 12x500ml", 6.40)],
                  "ZestUp": [("Orange Soda 330ml", 0.95), ("Lemon-Lime 330ml", 0.95), ("Cola Zero 1.5L", 2.10), ("Orange Soda 6x330ml", 5.20)],
                  "Kova": [("Peach Iced Tea 500ml", 1.45), ("Lemon Iced Tea 500ml", 1.45), ("Green Tea Honey 1L", 2.40)]},
    "Snacks": {"Crunchies": [("Sea Salt Chips 150g", 2.30), ("Cheddar Chips 150g", 2.30), ("Paprika Chips 45g", 0.90), ("Party Pack 300g", 4.20)],
               "Golden Grain": [("Oat Bar Honey 6pk", 3.60), ("Granola Crunch 400g", 4.80), ("Rice Crackers 100g", 1.90)]},
    "Dairy": {"Meadowfield": [("Whole Milk 1L", 1.35), ("Low-Fat Milk 1L", 1.35), ("Butter 250g", 3.20), ("Cheddar Block 400g", 5.40)],
              "Velora": [("Greek Yogurt 500g", 3.10), ("Strawberry Yogurt 4x125g", 2.70), ("Drinking Yogurt 250ml", 1.15)]},
    "Personal Care": {"Silkara": [("Shampoo Repair 400ml", 6.20), ("Conditioner Repair 400ml", 6.20), ("Hair Oil 150ml", 7.80)],
                      "PureGlow": [("Body Wash Citrus 500ml", 4.90), ("Hand Soap 300ml", 2.60), ("Face Cream SPF30 50ml", 11.50), ("Deodorant Roll-On 50ml", 3.40)]},
    "Home Care": {"Sparkle Home": [("Dish Liquid 750ml", 2.80), ("Surface Spray 500ml", 3.30), ("Laundry Liquid 2L", 9.90), ("Laundry Pods 30ct", 11.90)],
                  "EcoNest": [("Eco Dish Tabs 40ct", 8.90), ("Eco Glass Cleaner 500ml", 3.70), ("Eco Fabric Softener 1L", 4.60)]},
    "Confectionery": {"Cocoa Bliss": [("Milk Chocolate Bar 100g", 1.60), ("Dark Chocolate 70% 100g", 1.90), ("Praline Box 250g", 7.50), ("Mini Bars 12pk", 4.40)],
                      "Sweetbay": [("Fruit Gums 150g", 1.40), ("Mint Drops 50g", 0.85), ("Toffee Bag 200g", 2.20)]},
}

prod_rows = []
k = 1
for cat, bmap in brands.items():
    cogs_pct = categories[cat][0]
    for brand, skus in bmap.items():
        for name, price in skus:
            pack = "Multipack" if re.search(r"\d+x\d|\d+pk|\d+ct", name) else "Single"
            prod_rows.append({
                "ProductKey": k,
                "SKU": f"{cat[:3].upper()}-{brand[:3].upper()}-{k:03d}",
                "ProductName": f"{brand} {name}",
                "Brand": brand,
                "Category": cat,
                "Segment": "Premium" if price > np.median([p for _, p in skus]) * 1.25 else ("Value" if price < np.median([p for _, p in skus]) * 0.7 else "Mainstream"),
                "PackType": pack,
                "UnitListPrice": round(price, 2),
                "UnitCost": round(price * cogs_pct * rng.uniform(0.92, 1.06), 2),
                "LaunchDate": "2019-01-01" if k % 9 else "2024-03-01",
            })
            k += 1
dim_product = pd.DataFrame(prod_rows)

regions = [
    # key, region, director, weight
    (1, "North",   "Amira Haddad",   1.15),
    (2, "South",   "Daniel Okafor",  0.95),
    (3, "East",    "Priya Raman",    1.05),
    (4, "West",    "Lucas Moreau",   1.00),
    (5, "Central", "Sofia Lindqvist", 1.25),
    (6, "Coastal", "Kenji Watanabe", 0.70),
]
dim_region = pd.DataFrame(regions, columns=["RegionKey", "Region", "RegionalDirector", "_w"])
region_cities = {
    "North": ["Highmoor", "Ashby", "Northgate"], "South": ["Port Elia", "Sunvale", "Redcliff"],
    "East": ["Eastbrook", "Lindon", "Marlow"], "West": ["Westhaven", "Ironvale", "Pinecrest"],
    "Central": ["Capital City", "Midtown", "Riverside"], "Coastal": ["Bayview", "Saltmere", "Harborfield"],
}

channels = [
    # key, channel, group, base discount, weight, annual growth
    (1, "Modern Trade",       "Retail",      0.085, 1.00, 0.04),
    (2, "Traditional Trade",  "Retail",      0.050, 0.75, -0.01),
    (3, "E-Commerce",         "Digital",     0.065, 0.45, 0.28),
    (4, "Wholesale",          "B2B",         0.120, 0.85, 0.02),
    (5, "HoReCa",             "Out-of-Home", 0.070, 0.35, 0.06),
]
dim_channel = pd.DataFrame(channels, columns=["ChannelKey", "Channel", "ChannelGroup", "_disc", "_w", "_g"])

# Category affinity by channel (HoReCa sells little Personal Care etc.)
affinity = pd.DataFrame(1.0, index=list(categories), columns=dim_channel.Channel)
affinity.loc["Personal Care", "HoReCa"] = 0.15
affinity.loc["Home Care", "HoReCa"] = 0.55
affinity.loc["Beverages", "HoReCa"] = 1.9
affinity.loc["Personal Care", "E-Commerce"] = 1.6
affinity.loc["Confectionery", "Traditional Trade"] = 1.3
affinity.loc["Dairy", "E-Commerce"] = 0.7

cust_name_patterns = {
    "Modern Trade": ["{c} Hypermarket", "SuperSave {c}", "FreshMart {c}", "ValuePlus {c}"],
    "Traditional Trade": ["{c} Family Grocers", "Corner Store Co-op {c}", "{c} Mini Market"],
    "E-Commerce": ["QuickCart {r}", "BasketHub {r}", "ShopNest {r}"],
    "Wholesale": ["{c} Cash & Carry", "{r} Distribution Ltd", "Metro Wholesale {c}"],
    "HoReCa": ["{c} Hotels Group", "{c} Café Collective", "{r} Catering Services"],
}
cust_rows = []
ck = 1
for rkey, rname, *_ in regions:
    for chkey, chname, *_ in channels:
        n = {"Modern Trade": 4, "Traditional Trade": 3, "E-Commerce": 2, "Wholesale": 2, "HoReCa": 2}[chname]
        pats = cust_name_patterns[chname]
        for i in range(n):
            city = region_cities[rname][i % 3]
            name = pats[i % len(pats)].format(c=city, r=rname)
            size = float(np.round(rng.lognormal(0, 0.45), 3))
            tier = "Key Account" if size > 1.5 else ("Gold" if size > 1.0 else ("Silver" if size > 0.6 else "Bronze"))
            cust_rows.append({"CustomerKey": ck, "CustomerCode": f"C{ck:04d}", "CustomerName": name, "City": city,
                              "RegionKey": rkey, "ChannelKey": chkey, "CustomerTier": tier,
                              "CustomerSince": str(pd.Timestamp("2015-01-01") + pd.Timedelta(days=int(rng.integers(0, 3000))))[:10],
                              "_size": size})
            ck += 1
dim_customer = pd.DataFrame(cust_rows)

# --------------------------------------------------------------------------------------
# Demand model
# --------------------------------------------------------------------------------------
prod_cat = np.asarray(dim_product.Category, dtype=object)
P, C, M = len(dim_product), len(dim_customer), len(months)
prod_base = rng.lognormal(np.log(900), 0.55, P) / np.sqrt(dim_product.UnitListPrice.values)  # cheaper -> more units
cat_idx = {c: i for i, c in enumerate(categories)}
season = np.array([categories[c][1] for c in categories])            # cat x 12
cat_growth = np.array([categories[c][2] for c in categories])

cust_region = dim_customer.RegionKey.values
cust_channel = dim_customer.ChannelKey.values
reg_w = dim_region.set_index("RegionKey")._w
ch = dim_channel.set_index("ChannelKey")

# Listing matrix: which customer stocks which SKU
listing = rng.random((P, C)) < np.where(dim_customer._size.values > 1.0, 0.85, 0.6)[None, :]
listing &= ~((prod_cat[:, None] == "Personal Care") & (cust_channel[None, :] == 5) & (rng.random((P, C)) < 0.8))

years_from_start = np.array([(m.year - 2024) + (m.month - 1) / 12 for m in months])
month_no = np.array([m.month for m in months])

# expected units: P x C x M
lam = np.zeros((P, C, M))
for p in range(P):
    ci = cat_idx[prod_cat[p]]
    s = season[ci, month_no - 1]
    g = (1 + cat_growth[ci]) ** years_from_start
    for c in range(C):
        if not listing[p, c]:
            continue
        chk = cust_channel[c]
        chg = (1 + ch.loc[chk, "_g"]) ** years_from_start
        lam[p, c, :] = (prod_base[p] * s * g * chg * reg_w[cust_region[c]] * ch.loc[chk, "_w"]
                        * affinity.loc[prod_cat[p], ch.loc[chk, "Channel"]] * dim_customer._size.values[c] * 0.55)
# New SKUs launched Mar-2024 ramp up
launch = pd.to_datetime(dim_product.LaunchDate).values
for p in range(P):
    if launch[p] > np.datetime64("2023-12-31"):
        ramp = np.clip((np.arange(M) - 2) / 8, 0, 1)
        lam[p] *= ramp[None, :]

# Unforecasted shocks (the "story" in the variance analysis) ---------------------------
shock = np.ones((P, C, M))
def mi(y, m): return months.get_loc(pd.Timestamp(year=y, month=m, day=1))
def apply(cat, region=None, channel=None, ym=(), f=1.0):
    pm = prod_cat == cat
    cm = np.ones(C, bool)
    if region: cm &= cust_region == dim_region.set_index("Region").RegionKey[region]
    if channel: cm &= cust_channel == dim_channel.set_index("Channel").ChannelKey[channel]
    for y, m in ym:
        shock[np.ix_(pm, cm, [mi(y, m)])] *= f
apply("Beverages", region="North", ym=[(2026, 9), (2026, 10)], f=0.78)       # cool, wet autumn in the North
apply("Beverages", ym=[(2025, 7), (2025, 8)], f=1.12)                        # 2025 heatwave
apply("Personal Care", channel="E-Commerce", ym=[(2026, 10)], f=1.45)        # 10.10 online mega-sale
apply("Personal Care", channel="E-Commerce", ym=[(2025, 11)], f=1.35)
apply("Snacks", channel="Modern Trade", ym=[(2026, 8), (2026, 9), (2026, 10)], f=1.10)  # new shelf-space deal
apply("Dairy", region="Central", ym=[(2026, 6), (2026, 7)], f=0.86)          # supply disruption
apply("Home Care", channel="Wholesale", ym=[(2026, 10)], f=0.84)             # distributor destocking
apply("Confectionery", ym=[(2025, 12)], f=1.08)

# Actual units ---------------------------------------------------------------------------
noise = rng.lognormal(-0.016, 0.18, (P, C, M))
units_month = np.rint(lam * shock * noise).astype(int)
act_mask = np.array([m <= ACTUALS_END for m in months])
units_month[:, :, ~act_mask] = 0

# Price increases: +3.5% Apr-2025, +2.5% Apr-2026
price_idx = np.where(months >= pd.Timestamp("2026-04-01"), 1.035 * 1.025, np.where(months >= pd.Timestamp("2025-04-01"), 1.035, 1.0))
cost_idx = np.where(months >= pd.Timestamp("2026-01-01"), 1.045 * 1.03, np.where(months >= pd.Timestamp("2025-01-01"), 1.045, 1.0))

# Promotional months by category (deeper discount)
promo = np.zeros((len(categories), M))
for ci in range(len(categories)):
    promo[ci, rng.choice(M, 8, replace=False)] = rng.uniform(0.03, 0.07, 8)

# Explode to order lines -----------------------------------------------------------------
lines = []
order_no = 100000
p_idx, c_idx, m_idx = np.nonzero(units_month)
for p, c, m in zip(p_idx, c_idx, m_idx):
    u = units_month[p, c, m]
    mstart = months[m]
    days_in = mstart.days_in_month
    n_orders = int(min(max(1, rng.poisson(1.0 + dim_customer._size.values[c] * 0.8)), 4, u))
    split = rng.multinomial(u, rng.dirichlet(np.ones(n_orders) * 3))
    days = np.sort(rng.choice(np.arange(1, days_in + 1), n_orders, replace=False))
    chk = cust_channel[c]
    for d, uu in zip(days, split):
        if uu == 0:
            continue
        dt = mstart + pd.Timedelta(days=int(d) - 1)
        if dt.weekday() == 6:  # no Sunday deliveries
            dt -= pd.Timedelta(days=1)
            if dt.month != mstart.month:
                dt += pd.Timedelta(days=2)
        list_price = round(dim_product.UnitListPrice.values[p] * price_idx[m], 2)
        disc = max(0.0, ch.loc[chk, "_disc"] + promo[cat_idx[prod_cat[p]], m] + rng.normal(0, 0.012))
        gross = round(uu * list_price, 2)
        disc_amt = round(gross * disc, 2)
        cogs = round(uu * dim_product.UnitCost.values[p] * cost_idx[m] * rng.normal(1, 0.01), 2)
        order_no += 1
        lines.append((order_no, dt, p + 1, c + 1, int(cust_region[c]), int(chk), int(uu), list_price, gross, disc_amt, round(gross - disc_amt, 2), cogs))

fact_sales = pd.DataFrame(lines, columns=["OrderNumber", "OrderDate", "ProductKey", "CustomerKey", "RegionKey", "ChannelKey",
                                          "Units", "UnitListPrice", "GrossSales", "DiscountAmount", "NetSales", "COGS"])
fact_sales = fact_sales.sort_values(["OrderDate", "OrderNumber"]).reset_index(drop=True)
fact_sales.insert(0, "SalesLineID", np.arange(1, len(fact_sales) + 1))
fact_sales["OrderNumber"] = "SO-" + fact_sales.OrderNumber.astype(str)
fact_sales["OrderDate"] = fact_sales.OrderDate.dt.strftime("%Y-%m-%d")

# --------------------------------------------------------------------------------------
# Forecast & budget: month x SKU x region x channel
# --------------------------------------------------------------------------------------
grain = []
lam_rc = {}
for r in dim_region.RegionKey:
    for chk in dim_channel.ChannelKey:
        cm = (cust_region == r) & (cust_channel == chk)
        lam_rc[(r, chk)] = lam[:, cm, :].sum(axis=1)  # P x M (no shocks: they're unforecastable)

cat_bias_fc = {c: b for c, b in zip(categories, rng.normal(0.01, 0.025, len(categories)))}
cat_bias_bud = {2024: rng.normal(0.02, 0.04, len(categories)), 2025: rng.normal(0.03, 0.04, len(categories)), 2026: rng.normal(0.035, 0.04, len(categories))}
avg_disc = ch._disc

for (r, chk), L in lam_rc.items():
    for p in range(P):
        if L[p].sum() == 0:
            continue
        ci = cat_idx[prod_cat[p]]
        fc_units = L[p] * (1 + cat_bias_fc[prod_cat[p]]) * rng.lognormal(0, 0.075, M)
        bud_units = L[p] * np.array([1 + cat_bias_bud[m.year][ci] for m in months]) * rng.lognormal(0, 0.05, M)
        # budget doesn't know about e-com acceleration in 2026 -> under-budgets e-com
        if chk == 3:
            bud_units *= np.where(months.year == 2026, 0.90, 1.0)
        lp = dim_product.UnitListPrice.values[p]
        uc = dim_product.UnitCost.values[p]
        for m in range(M):
            if fc_units[m] < 0.5 and bud_units[m] < 0.5:
                continue
            # Budget assumed a 3% price increase in 2026 vs actual 2.5%
            bud_price = lp * (1.035 if months[m].year >= 2025 else 1.0) * (1.03 if months[m].year == 2026 else 1.0)
            net_px_fc = lp * price_idx[m] * (1 - avg_disc[chk] - 0.02)
            net_px_bud = bud_price * (1 - avg_disc[chk] - 0.02)
            grain.append((months[m].strftime("%Y-%m-%d"), p + 1, int(r), int(chk),
                          int(round(fc_units[m])), round(fc_units[m] * net_px_fc, 2), round(fc_units[m] * uc * cost_idx[m], 2),
                          int(round(bud_units[m])), round(bud_units[m] * net_px_bud, 2), round(bud_units[m] * uc * cost_idx[m] * 0.99, 2)))

fact_forecast = pd.DataFrame(grain, columns=["MonthStartDate", "ProductKey", "RegionKey", "ChannelKey",
                                             "ForecastUnits", "ForecastNetSales", "ForecastCOGS",
                                             "BudgetUnits", "BudgetNetSales", "BudgetCOGS"])
fact_forecast.insert(0, "ForecastLineID", np.arange(1, len(fact_forecast) + 1))
fact_forecast.insert(2, "ForecastVersion", "Rolling Forecast (Latest)")

# --------------------------------------------------------------------------------------
# Write
# --------------------------------------------------------------------------------------
dim_product.to_csv(os.path.join(OUT, "dim_product.csv"), index=False)
dim_customer.drop(columns=["_size"]).to_csv(os.path.join(OUT, "dim_customer.csv"), index=False)
dim_region.drop(columns=["_w"]).to_csv(os.path.join(OUT, "dim_region.csv"), index=False)
dim_channel.drop(columns=["_disc", "_w", "_g"]).to_csv(os.path.join(OUT, "dim_channel.csv"), index=False)
fact_sales.to_csv(os.path.join(OUT, "fact_sales.csv"), index=False)
fact_forecast.to_csv(os.path.join(OUT, "fact_forecast.csv"), index=False)

print(f"products={len(dim_product)} customers={len(dim_customer)} sales_lines={len(fact_sales):,} forecast_lines={len(fact_forecast):,}")
print("Net sales by year:", fact_sales.assign(y=fact_sales.OrderDate.str[:4]).groupby("y").NetSales.sum().round(0).to_dict())
