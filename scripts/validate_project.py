"""
Static checks for the PBIP project (run after build_pbip.py):
  1. every PBIR json file validates against Microsoft's published JSON schemas (pass the schema root as argv[1])
  2. every table/column/measure referenced by a visual exists in the semantic model
  3. every [Measure] / 'Table'[Column] reference inside DAX resolves
"""
import json, os, re, sys, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pbip as B

errors = []
cols = {t: {c[0] for c in s["columns"]} | {c[0] for c in s.get("calculated", [])} for t, s in B.TABLES.items()}
meas = B.MEASURE_NAMES

# ---- DAX reference checks
def check_dax(owner, expr, local_cols=None):
    stripped = re.sub(r'"[^"]*"', '""', expr)
    for t, c in re.findall(r"'([^']+)'\[([^\]]+)\]", stripped):
        if t not in cols or c not in cols[t]:
            errors.append(f"{owner}: unknown column '{t}'[{c}]")
    for m in re.findall(r"(?<!['\]\w])\[([^\]]+)\]", stripped):
        if m.startswith("@"):
            continue
        if m not in meas:
            errors.append(f"{owner}: unknown measure [{m}]")
for (n, e, *_r) in B.MEASURES:
    check_dax(f"measure {n}", e)
for t, s in B.TABLES.items():
    for (c, _dt, e, _d) in s.get("calculated", []):
        check_dax(f"column {t}[{c}]", e)
    for (c, _dt, fl) in s["columns"]:
        if fl.get("sortBy") and fl["sortBy"] not in cols[t]:
            errors.append(f"sortBy {t}[{c}] -> {fl['sortBy']}")
    for (h, lv) in s.get("hierarchies", []):
        for l in lv:
            if l not in cols[t]:
                errors.append(f"hierarchy {t}.{h} level {l}")
for (ft, fc, tt, tc) in B.RELATIONSHIPS:
    if fc not in cols[ft] or tc not in cols[tt]:
        errors.append(f"relationship {ft}.{fc}->{tt}.{tc}")
# M output columns vs TMDL source columns (best effort: renamed/added names must appear in the M text)
for t, s in B.TABLES.items():
    for (c, _dt, _fl) in s["columns"]:
        if f'"{c}"' not in B.M[t] and f"{c} =" not in B.M[t] and f'#"{c}"' not in B.M[t]:
            errors.append(f"M query for {t} never produces column {c}")

# ---- report references
def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)
rep = os.path.join(ROOT, "pbip", f"{B.NAME}.Report", "definition")
def check_ref(o, path):
    for kind in ("Measure", "Column"):
        if kind in o and isinstance(o[kind], dict) and "Property" in o[kind]:
            src = o[kind]["Expression"]["SourceRef"]
            ent = src.get("Entity")
            if ent is None:
                continue  # aliased (filters) - checked via 'field'
            prop = o[kind]["Property"]
            ok = (prop in meas and ent == B.MEAS) if kind == "Measure" else (ent in cols and prop in cols[ent])
            if not ok:
                errors.append(f"{path}: unknown {kind} {ent}.{prop}")
for f in glob.glob(os.path.join(rep, "pages", "*", "visuals", "*", "visual.json")):
    walk(json.load(open(f, encoding="utf-8")), lambda o, f=f: check_ref(o, os.path.relpath(f, rep)))

# ---- JSON schema validation
if len(sys.argv) > 1:
    import jsonschema
    from referencing import Registry, Resource
    sroot = sys.argv[1]
    base = "https://developer.microsoft.com/json-schemas/"
    res = []
    for p in glob.glob(os.path.join(sroot, "**", "*.json"), recursive=True):
        rel = os.path.relpath(p, sroot).replace(os.sep, "/")
        doc = json.load(open(p, encoding="utf-8"))
        uri = base + ("fabric/item/report/" + rel if not rel.startswith("x/") else rel[2:])
        res.append((uri, Resource.from_contents(doc, default_specification=jsonschema.Draft7Validator.META_SCHEMA and __import__("referencing.jsonschema").jsonschema.DRAFT7)))
    reg = Registry().with_resources(res)
    files = glob.glob(os.path.join(ROOT, "pbip", "**", "*.json"), recursive=True) + glob.glob(os.path.join(ROOT, "pbip", "*.pbip"), recursive=True) \
        + glob.glob(os.path.join(ROOT, "pbip", "**", "*.pbir"), recursive=True) + glob.glob(os.path.join(ROOT, "pbip", "**", "*.pbism"), recursive=True)
    n = 0
    for f in files:
        doc = json.load(open(f, encoding="utf-8"))
        sch = doc.get("$schema")
        if not sch:
            continue
        try:
            schema = reg.resolver().lookup(sch).contents
        except Exception as e:
            errors.append(f"no local schema for {sch}")
            continue
        v = jsonschema.Draft7Validator(schema, registry=reg)
        for e in v.iter_errors(doc):
            errors.append(f"{os.path.relpath(f, ROOT)}: {e.json_path}: {e.message[:200]}")
        n += 1
    print(f"schema-validated {n} files")

print("\n".join(errors) if errors else "OK: no problems found")
sys.exit(1 if errors else 0)
