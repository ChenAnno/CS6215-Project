#!/usr/bin/env python3
"""Generate the tables of the report from results/ (report/tables/*.tex, results/tables.md).

    .venv/bin/python -I eval/tables.py
"""

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
import subjects  # noqa: E402

RES = PROJECT / "results"
TEX = PROJECT / "report" / "tables"
TEX.mkdir(parents=True, exist_ok=True)
MD = []

ROWS = [
    ("pycg-2021", "PyCG-2021 (baseline)"),
    ("pycg-2026", "PyCG-2026 (baseline)"),
    ("nscg-sym", "S1 only (no LLM)"),
    ("llm-only", "V0 LLM-only"),
    ("nscg-nohints", "V1 sites, no hints"),
    ("nscg", "V2 NSCG"),
    ("nscg-v21", "V2.1 NSCG (final)"),
    ("nscg-hybrid", "V3 hybrid (V2+PyCG)"),
    ("nscg-hybrid-v21", "V3 hybrid (V2.1+PyCG)"),
    ("union--pycg-2026--nscg-v21", "PyCG-2026 $\\cup$ V2.1"),
    ("inter--pycg-2026--nscg-v21", "PyCG-2026 $\\cap$ V2.1"),
    ("llm-only@sonnet", "V0 LLM-only, Sonnet"),
    ("nscg-v21@sonnet", "V2.1 NSCG, Sonnet"),
]


def load(tool):
    p = RES / "scores" / f"{tool}.json"
    return json.loads(p.read_text()) if p.exists() else None


def f1(p, r):
    if p is None or r is None:
        return None
    return 2 * p * r / (p + r) if p + r else 0.0


def fmt(x, d=3):
    return "--" if x is None else f"{x:.{d}f}"


def counts_pr(c):
    p = c["tp"] / c["tool"] if c["tool"] else None
    r = c["tp"] / c["truth"] if c["truth"] else None
    return p, r, f1(p, r)


def sum_counts(cs):
    out = {"tool": 0, "truth": 0, "tp": 0}
    for c in cs:
        for k in out:
            out[k] += c[k]
    return out


def best_marks(values):
    """Indices of the best value per column (bold)."""
    vals = [v for v in values if v is not None]
    return max(vals) if vals else None


def write(name, text):
    (TEX / f"{name}.tex").write_text(text)


# ---------------------------------------------------------------- main table
def main_table():
    lines = []
    md = ["| Tool | micro in P | R | F1 | micro out P | R | exact | macro in P | R | F1 | macro out P | R | F1 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    data = []
    for tool, label in ROWS:
        s = load(tool)
        if s is None:
            continue
        row = [label]
        mi = s.get("micro", {}).get("total")
        if mi:
            p, r, f = counts_pr(mi["inside"])
            po, ro, _ = counts_pr(mi["outside"])
            row += [p, r, f, po, ro, mi["exact"]]
        else:
            row += [None] * 6
        ma = s.get("macro_total")
        if ma:
            p, r, f = counts_pr(ma["inside"])
            po, ro, fo = counts_pr(ma["outside"])
            row += [p, r, f, po, ro, fo]
        else:
            row += [None] * 6
        data.append((tool, row))
    cols = list(zip(*[r for _, r in data]))[1:]
    best = [best_marks(c) for c in cols]
    for tool, row in data:
        cells = [row[0]]
        md.append("| " + " | ".join([row[0]] + [fmt(v) if i != 5 else (str(v) if v is not None else "--")
                                                for i, v in enumerate(row[1:])]) + " |")
        for i, v in enumerate(row[1:]):
            t = (str(v) if v is not None else "--") if i == 5 else fmt(v, 3)
            if v is not None and v == best[i] and not tool.startswith(("union", "inter")) and "sonnet" not in tool:
                t = "\\textbf{" + t + "}"
            cells.append(t)
        lines.append(" & ".join(cells) + " \\\\")
        if tool in ("pycg-2026", "nscg-hybrid-v21", "inter--pycg-2026--nscg-v21"):
            lines.append("\\midrule")
    while lines and lines[-1] == "\\midrule":
        lines.pop()
    tex = ("\\begin{tabular}{l rrr rr r rrr rrr}\n\\toprule\n"
           "& \\multicolumn{6}{c}{Micro-benchmark (622 cases)} & \\multicolumn{6}{c}{Four packages (1,973 sites)}\\\\\n"
           "\\cmidrule(lr){2-7}\\cmidrule(lr){8-13}\n"
           "& \\multicolumn{3}{c}{inside} & \\multicolumn{2}{c}{outside} & & \\multicolumn{3}{c}{inside} & \\multicolumn{3}{c}{outside}\\\\\n"
           "\\cmidrule(lr){2-4}\\cmidrule(lr){5-6}\\cmidrule(lr){8-10}\\cmidrule(lr){11-13}\n"
           "Tool & P & R & F1 & P & R & exact & P & R & F1 & P & R & F1\\\\\n\\midrule\n"
           + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("main", tex)
    MD.append("## Main results\n\n" + "\n".join(md))


# ---------------------------------------------------------------- per project
PROJ_ROWS = [("pycg-2021", "PyCG-2021"), ("pycg-2026", "PyCG-2026"), ("nscg-sym", "S1 only"),
             ("llm-only", "V0"), ("nscg", "V2"), ("nscg-v21", "V2.1"), ("nscg-hybrid-v21", "V3 (V2.1)"),
             ("union--pycg-2026--nscg-v21", "$\\cup$")]


def project_table():
    projs = subjects.SELECTED
    lines, md = [], ["| Tool | " + " | ".join(projs) + " |", "|---|" + "---|" * len(projs)]
    for tool, label in PROJ_ROWS:
        s = load(tool)
        if s is None or "macro" not in s:
            continue
        cells, mcells = [label], [label]
        for pname in projs:
            r = s["macro"][pname]
            if r["status"] != "ok":
                cells += ["\\multicolumn{3}{c}{" + r["status"].split(":")[0] + "}"]
                mcells.append(r["status"])
                continue
            p, rc, f = counts_pr(r["inside"])
            cells += [fmt(p, 2), fmt(rc, 2), fmt(f, 2)]
            mcells.append(f"{fmt(p)}/{fmt(rc)}/{fmt(f)}")
        lines.append(" & ".join(cells) + " \\\\")
        md.append("| " + " | ".join(mcells) + " |")
    head = " & ".join("\\multicolumn{3}{c}{" + p + "}" for p in projs)
    rule = "".join(f"\\cmidrule(lr){{{2 + 3 * i}-{4 + 3 * i}}}" for i in range(len(projs)))
    sub = " & ".join(["P & R & F1"] * len(projs))
    tex = ("\\begin{tabular}{l " + "rrr " * len(projs) + "}\n\\toprule\n& " + head + "\\\\\n" + rule + "\n& " + sub
           + "\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("projects", tex)
    MD.append("## Per project, inside edges (P/R/F1)\n\n" + "\n".join(md))


# ---------------------------------------------------------------- subjects
def subjects_table():
    import importlib.util

    spec = importlib.util.spec_from_file_location("mp", subjects.MACRO / "projects.py")
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    projs = mp.load_projects()
    base = load("pycg-2026")
    lines, md = [], ["| Package | batch | LOC | modules | nodes | edges in/out | sites | PyCG-2026 F1 in |",
                     "|---|---|---|---|---|---|---|---|"]
    for name in subjects.SELECTED:
        pr = projs[name]
        files = pr.source_files()
        loc = sum(len(Path(f).read_text(errors="replace").splitlines()) for f in files)
        truth = json.loads((subjects.MACRO / "ground-truth" / f"{name}.json").read_text())
        pk = pr.package_names
        inside = sum(1 for k, vs in truth.items() for v in vs if any(v == p or v.startswith(p + ".") for p in pk))
        total = sum(len(vs) for vs in truth.values())
        raw = json.loads((RES / "raw" / "nscg-sym" / "macro" / f"{name}.json").read_text())
        sites = sum(len(u["sites"]) for u in raw["units"])
        f = counts_pr(base["macro"][name]["inside"])[2] if base else None
        batch = "ICSE'21" if pr.batch == "icse-2021" else str(pr.batch)
        lines.append(f"{name} & {batch} & {loc:,} & {len(files)} & {len(truth)} & {inside}/{total - inside} & {sites} & {fmt(f, 2)} \\\\")
        md.append(f"| {name} | {batch} | {loc} | {len(files)} | {len(truth)} | {inside}/{total - inside} | {sites} | {fmt(f)} |")
    tex = ("\\begin{tabular}{l l r r r r r r}\n\\toprule\nPackage & batch & LOC & mod. & nodes & edges in/out & sites & PyCG F1\\\\\n"
           "\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("subjects", tex)
    MD.append("## Subjects\n\n" + "\n".join(md))


# ---------------------------------------------------------------- cost
COST_ROWS = [("nscg", "V2"), ("llm-only", "V0"), ("nscg-nohints", "V1"), ("nscg-hybrid", "V3 (V2)"),
             ("nscg-v21", "V2.1"), ("nscg-hybrid-v21", "V3 (V2.1)"), ("nscg-v21-r1", "V2.1 rep.~2"),
             ("nscg-v21-r2", "V2.1 rep.~3"), ("nscg-v21@sonnet", "V2.1 Sonnet"), ("llm-only@sonnet", "V0 Sonnet"),
             ("nscg-v21+renamed", "V2.1 renamed"), ("llm-only+renamed", "V0 renamed")]


def cost_table():
    """Cost of the requests each run really sent: a cached answer is counted once, for the first run
    (in the order of COST_ROWS, the order in which the runs were made) that needed it."""
    lines, md = [], ["| Run | benchmark | new requests | input tok (incl. cache) | output tok | cost USD | wall s |",
                     "|---|---|---|---|---|---|---|"]
    tot, seen = 0.0, set()
    totals = {"req": 0, "itok": 0, "otok": 0}
    for tool, label in COST_ROWS:
        for bench in ("micro", "macro"):
            p = RES / "runs" / f"{tool}-{bench}.json"
            if not p.exists():
                continue
            r = json.loads(p.read_text())
            units = [u for u in r["per_unit"].values() if u.get("cache_key") not in seen]
            seen |= {u.get("cache_key") for u in r["per_unit"].values()}
            cost = sum((u.get("cost_usd") or 0) for u in units)
            itok = sum((u.get("usage") or {}).get("input_tokens", 0) + (u.get("usage") or {}).get("cache_read_input_tokens", 0)
                       + (u.get("usage") or {}).get("cache_creation_input_tokens", 0) for u in units)
            otok = sum((u.get("usage") or {}).get("output_tokens", 0) for u in units)
            tot += cost
            totals["req"] += len(units)
            totals["itok"] += itok
            totals["otok"] += otok
            lines.append(f"{label} & {bench} & {len(units)} & {itok / 1e6:.2f}M & {otok / 1e3:.0f}k & {cost:.2f} & {r['wall_seconds']:.0f} \\\\")
            md.append(f"| {label} | {bench} | {len(units)} | {itok} | {otok} | {cost:.3f} | {r['wall_seconds']} |")
    lines.append(f"\\midrule\nTotal & & {totals['req']} & {totals['itok'] / 1e6:.2f}M & {totals['otok'] / 1e3:.0f}k & {tot:.2f} & \\\\")
    md.append(f"| Total | | {totals['req']} | {totals['itok']} | {totals['otok']} | {tot:.3f} | |")
    tex = ("\\begin{tabular}{l l r r r r r}\n\\toprule\nRun & bench. & req. & input tok. & output tok. & USD & wall s\\\\\n"
           "\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("cost", tex)
    (TEX / "total_cost.tex").write_text(f"{tot:.2f}")
    MD.append("## Cost\n\n" + "\n".join(md))
    return tot


# ---------------------------------------------------------------- validation / errors
def errors_table():
    rows = [("nscg-sym", "S1 only"), ("llm-only", "V0"), ("nscg", "V2"), ("nscg-v21", "V2.1"),
            ("nscg-hybrid-v21", "V3 (V2.1)")]
    labs = ["fn-no-evidence", "fn-rejected", "fn-ext-misnamed", "fn-ext-omitted", "fp-accepted-hint", "fp-llm-added",
            "fp-ext-misnamed", "fp-ext-spurious"]
    lines, md = [], ["| Tool | " + " | ".join(labs) + " |", "|---|" + "---|" * len(labs)]
    for tool, label in rows:
        p = RES / "errors" / f"{tool}-macro.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())["summary"]
        lines.append(label + " & " + " & ".join(str(d.get(l, 0)) for l in labs) + " \\\\")
        md.append(f"| {label} | " + " | ".join(str(d.get(l, 0)) for l in labs) + " |")
    tex = ("\\begin{tabular}{l rrrr rrrr}\n\\toprule\n& \\multicolumn{4}{c}{false negatives} & \\multicolumn{4}{c}{false positives}\\\\\n"
           "\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}\n& \\multicolumn{2}{c}{inside} & \\multicolumn{2}{c}{outside} & \\multicolumn{2}{c}{inside} & \\multicolumn{2}{c}{outside}\\\\\n"
           "Tool & no hint & dropped & misnamed & omitted & from hint & added & misnamed & spurious\\\\\n\\midrule\n"
           + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("errors", tex)
    MD.append("## Error taxonomy (macro)\n\n" + "\n".join(md))


def validation_table():
    rows = [("nscg", "V2"), ("nscg-v21", "V2.1"), ("nscg-nohints", "V1")]
    keys = ["kept-internal", "kept-external", "rejected-unknown-internal", "repaired-path", "class->constructor",
            "inherited->definer", "init->constructor", "rejected-external-at-implicit", "builtins->builtin", "floor-added"]
    md = ["| Run | bench | " + " | ".join(keys) + " |", "|---|---|" + "---|" * len(keys)]
    lines = []
    for tool, label in rows:
        for bench in ("micro", "macro"):
            p = RES / "runs" / f"{tool}-{bench}.json"
            if not p.exists():
                continue
            v = json.loads(p.read_text())["validation"]
            md.append(f"| {label} | {bench} | " + " | ".join(str(v.get(k, 0)) for k in keys) + " |")
            lines.append(f"{label} & {bench} & " + " & ".join(str(v.get(k, 0)) for k in keys) + " \\\\")
    short = ["kept in", "kept out", "rejected", "repaired", "cls$\\to$ctor", "inh.$\\to$def", "init$\\to$ctor",
             "out@impl.", "builtins", "floor"]
    tex = ("\\begin{tabular}{l l " + "r" * len(keys) + "}\n\\toprule\nRun & bench. & " + " & ".join(short)
           + "\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    write("validation", tex)
    MD.append("## Validation decisions\n\n" + "\n".join(md))


# ---------------------------------------------------------------- memorisation probe
def probe_table():
    pert = RES / "perturbed" / "micro-perturbation.json"
    if not pert.exists():
        return
    cohort = set(json.loads(pert.read_text())["cohort"])
    rows = [("pycg-2026", "PyCG-2026"), ("pycg-2021", "PyCG-2021"), ("nscg-sym", "S1 only"), ("llm-only", "V0 LLM-only"),
            ("nscg-v21", "V2.1 NSCG")]
    lines, md = [], ["| Tool | original P/R/F1 (inside) | renamed P/R/F1 | exact orig/renamed |", "|---|---|---|---|"]
    for tool, label in rows:
        o, rn = load(tool), load(tool + "+renamed")
        if not o or not rn or "micro" not in rn:
            continue
        oc = sum_counts([v["inside"] for k, v in o["micro"]["cases"].items() if k in cohort and "inside" in v])
        rc = sum_counts([v["inside"] for k, v in rn["micro"]["cases"].items() if k in cohort and "inside" in v])
        oa = sum_counts([v["all"] for k, v in o["micro"]["cases"].items() if k in cohort and "all" in v])
        ra = sum_counts([v["all"] for k, v in rn["micro"]["cases"].items() if k in cohort and "all" in v])
        oe = sum(1 for k, v in o["micro"]["cases"].items() if k in cohort and v.get("exact"))
        re_ = sum(1 for k, v in rn["micro"]["cases"].items() if k in cohort and v.get("exact"))
        a, b = counts_pr(oc), counts_pr(rc)
        fa, fb = counts_pr(oa)[2], counts_pr(ra)[2]
        NUMBERS[f"probe-orig-f1-{tool}"], NUMBERS[f"probe-ren-f1-{tool}"] = fmt(a[2]), fmt(b[2])
        NUMBERS[f"probe-orig-exact-{tool}"], NUMBERS[f"probe-ren-exact-{tool}"] = str(oe), str(re_)
        lines.append(f"{label} & {fmt(a[0])} & {fmt(a[1])} & {fmt(a[2])} & {fmt(b[0])} & {fmt(b[1])} & {fmt(b[2])} & "
                     f"{fmt(fa)} & {fmt(fb)} & {oe} & {re_} \\\\")
        md.append(f"| {label} | {fmt(a[0])}/{fmt(a[1])}/{fmt(a[2])} | {fmt(b[0])}/{fmt(b[1])}/{fmt(b[2])} | all-edge F1 {fmt(fa)} -> {fmt(fb)}; exact {oe} -> {re_} |")
    tex = ("\\begin{tabular}{l rrr rrr rr rr}\n\\toprule\n& \\multicolumn{3}{c}{original, inside} & \\multicolumn{3}{c}{renamed, inside}"
           " & \\multicolumn{2}{c}{all-edge F1} & \\multicolumn{2}{c}{exact}\\\\\n\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\\cmidrule(lr){8-9}\\cmidrule(lr){10-11}\n"
           "Tool & P & R & F1 & P & R & F1 & orig. & ren. & orig. & ren.\\\\\n\\midrule\n" + "\n".join(lines)
           + "\n\\bottomrule\n\\end{tabular}\n")
    write("probe", tex)
    MD.append(f"## Memorisation probe ({len(cohort)} renamed cases)\n\n" + "\n".join(md))


# ---------------------------------------------------------------- repetitions
def repeat_table():
    tools = ["nscg-v21", "nscg-v21-r1", "nscg-v21-r2"]
    ss = [load(t) for t in tools]
    if any(s is None or "macro_total" not in s for s in ss):
        return
    md = ["| metric | run 0 | run 1 | run 2 | mean | stdev |", "|---|---|---|---|---|---|"]
    lines = []
    for es in ("inside", "outside"):
        for i, m in enumerate(("P", "R", "F1")):
            vals = [counts_pr(s["macro_total"][es])[i] for s in ss]
            md.append(f"| {es} {m} | " + " | ".join(fmt(v) for v in vals) + f" | {fmt(statistics.mean(vals))} | {fmt(statistics.stdev(vals))} |")
            lines.append(f"{es} {m} & " + " & ".join(fmt(v) for v in vals) + f" & {fmt(statistics.mean(vals))} & {fmt(statistics.stdev(vals))} \\\\")
    # edge-level agreement between runs (inside, all projects)
    def edges(t):
        out = set()
        for name in subjects.SELECTED:
            g = json.loads((RES / "tools" / t / "macro" / f"{name}.json").read_text())
            out |= {(a, b) for a, bs in g.items() for b in bs}
        return out
    f1s = [counts_pr(s["macro_total"]["inside"])[2] for s in ss]
    ps_ = [counts_pr(s["macro_total"]["inside"])[0] for s in ss]
    rs_ = [counts_pr(s["macro_total"]["inside"])[1] for s in ss]
    NUMBERS["repeat-mean-f1"], NUMBERS["repeat-sd-f1"] = fmt(statistics.mean(f1s)), fmt(statistics.stdev(f1s))
    NUMBERS["repeat-min-p"], NUMBERS["repeat-max-p"] = fmt(min(ps_)), fmt(max(ps_))
    NUMBERS["repeat-min-r"], NUMBERS["repeat-max-r"] = fmt(min(rs_)), fmt(max(rs_))
    e = [edges(t) for t in tools]
    inter, union = set.intersection(*e), set.union(*e)
    md.append(f"\nEdges reported by all three runs: {len(inter)} of {len(union)} reported by any ({len(inter) / len(union):.3f}).")
    write("repeats", "\\begin{tabular}{l rrr rr}\n\\toprule\nMetric (4 packages) & run 1 & run 2 & run 3 & mean & s.d.\\\\\n\\midrule\n"
          + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    (TEX / "repeats_agreement.tex").write_text(f"{len(inter)} of {len(union)}")
    NUMBERS["repeat-agree"] = f"{len(inter)} of {len(union)}"
    NUMBERS["repeat-agree-pct"] = f"{100 * len(inter) / len(union):.0f}"
    MD.append("## Repetitions of V2.1 on the four packages\n\n" + "\n".join(md))


def overlap_numbers():
    p = RES / "errors" / "nscg-v21-macro.json"
    if p.exists():
        d = json.loads(p.read_text())
        MD.append("## Overlap of V2.1 errors with PyCG-2026 (macro)\n\n" + json.dumps(d.get("overlap_with_pycg-2026"), indent=1))


def category_table():
    tools = [("pycg-2026", "PyCG-26"), ("pycg-2021", "PyCG-21"), ("llm-only", "V0"), ("nscg-v21", "V2.1")]
    ss = {t: load(t) for t, _ in tools}
    if any(v is None for v in ss.values()):
        return
    cats = sorted(ss["pycg-2026"]["micro"]["categories"])
    md = ["| category | cases | " + " | ".join(l for _, l in tools) + " |", "|---|---|" + "---|" * len(tools)]
    data = {}
    for c in cats:
        row = []
        for t, _ in tools:
            cc = ss[t]["micro"]["categories"][c]["all"]
            row.append(counts_pr(cc)[2])
        data[c] = row
        md.append(f"| {c} | {ss['pycg-2026']['micro']['categories'][c]['cases']} | " + " | ".join(fmt(v) for v in row) + " |")
    MD.append("## Micro per category, all-edge F1\n\n" + "\n".join(md))
    (RES / "micro_categories.json").write_text(json.dumps({"tools": [l for _, l in tools], "rows": data,
                                                          "cases": {c: ss['pycg-2026']['micro']['categories'][c]['cases'] for c in cats}}, indent=1))


NUMBERS = {}


def numbers():
    """report/numbers.tex: every number quoted in the text, as \\R{key}."""
    allt = [t for t, _ in ROWS] + ["nscg-v21-r1", "nscg-v21-r2", "nscg-hybrid", "nscg-nohints"]
    for t in dict.fromkeys(allt):
        s = load(t)
        if s is None:
            continue
        if "micro" in s:
            tot = s["micro"]["total"]
            for es in ("inside", "outside", "all"):
                p, r, f = counts_pr(tot[es])
                NUMBERS[f"micro-{es[:3]}-p-{t}"], NUMBERS[f"micro-{es[:3]}-r-{t}"], NUMBERS[f"micro-{es[:3]}-f1-{t}"] = fmt(p), fmt(r), fmt(f)
                NUMBERS[f"micro-{es[:3]}-fp-{t}"] = str(tot[es]["fp"])
                NUMBERS[f"micro-{es[:3]}-fn-{t}"] = str(tot[es]["fn"])
            NUMBERS[f"micro-exact-{t}"] = str(tot["exact"])
            NUMBERS[f"micro-sound-{t}"] = str(tot["sound"])
            NUMBERS[f"micro-complete-{t}"] = str(tot["complete"])
        if "macro_total" in s:
            for es in ("inside", "outside"):
                p, r, f = counts_pr(s["macro_total"][es])
                NUMBERS[f"macro-{es[:3]}-p-{t}"], NUMBERS[f"macro-{es[:3]}-r-{t}"], NUMBERS[f"macro-{es[:3]}-f1-{t}"] = fmt(p), fmt(r), fmt(f)
                NUMBERS[f"macro-{es[:3]}-tp-{t}"] = str(s["macro_total"][es]["tp"])
                NUMBERS[f"macro-{es[:3]}-fp-{t}"] = str(s["macro_total"][es]["fp"])
                NUMBERS[f"macro-{es[:3]}-fn-{t}"] = str(s["macro_total"][es]["fn"])
            for name in subjects.SELECTED:
                r = s["macro"][name]
                p, rc, f = counts_pr(r["inside"])
                NUMBERS[f"{name}-in-p-{t}"], NUMBERS[f"{name}-in-r-{t}"], NUMBERS[f"{name}-in-f1-{t}"] = fmt(p), fmt(rc), fmt(f)
                NUMBERS[f"{name}-in-fn-{t}"] = str(r["inside"]["fn"])
                NUMBERS[f"{name}-in-fp-{t}"] = str(r["inside"]["fp"])
                NUMBERS[f"{name}-status-{t}"] = r["status"].split(":")[0]
    for t in ("nscg-sym", "llm-only", "nscg", "nscg-v21", "nscg-hybrid-v21", "nscg-nohints"):
        p = RES / "errors" / f"{t}-macro.json"
        if p.exists():
            d = json.loads(p.read_text())
            for k, v in d["summary"].items():
                NUMBERS[f"err-{k}-{t}"] = str(v)
            for k, v in d.get("overlap_with_pycg-2026", {}).items():
                NUMBERS[f"ovl-{k}-{t}"] = str(v)
    lines = ["% generated by eval/tables.py; use \\R{key}", "\\makeatletter"]
    for k, v in sorted(NUMBERS.items()):
        lines.append(f"\\expandafter\\def\\csname res@{k}\\endcsname{{{v}}}")
    lines += ["\\makeatother", "\\newcommand{\\R}[1]{\\ifcsname res@#1\\endcsname\\csname res@#1\\endcsname\\else\\textbf{??#1}\\fi}"]
    (PROJECT / "report" / "numbers.tex").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main_table()
    project_table()
    subjects_table()
    tot = cost_table()
    errors_table()
    validation_table()
    probe_table()
    repeat_table()
    overlap_numbers()
    category_table()
    numbers()
    (RES / "tables.md").write_text("# Results tables (generated by eval/tables.py)\n\n" + "\n\n".join(MD) + "\n")
    print("\n\n".join(MD))
