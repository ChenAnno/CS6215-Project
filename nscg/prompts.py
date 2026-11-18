"""Prompt templates of NSCG (all LLM-facing text lives here).

CONVENTIONS is the "skill" handed to the model: a condensed restatement of the call-graph
semantics that the benchmark's ground truth follows (node names, which calls are edges,
how callees outside the package are named). It is shared by every variant so that the
variants differ only in the symbolic information they receive.
"""

SYSTEM = (
    "You are the neural component of a neuro-symbolic static call-graph analyzer for Python. "
    "You reason about source code without running it. You answer only with the requested JSON."
)

CONVENTIONS = """\
## Call-graph semantics (follow exactly)
Nodes: modules, functions, methods and lambdas of the analysed package. Classes, class bodies and
comprehensions are NOT nodes. Names are dotted: module path (a package `__init__.py` is the package
name), then enclosing functions/classes: `pkg.mod.Class.method`, `pkg.mod.outer.inner`. Lambdas are
`<lambdaN>`, numbered from 1 by source position inside the scope that evaluates them
(`main.<lambda1>`, `main.f.<lambda2>`).
Edge A -> B: code of A can call B when A runs (any input a client could pass through the public API,
on any supported Python version).
- Calls in a class body, a comprehension, a default value or a decorator expression belong to the
  enclosing function or module.
- Instantiating a package class `C()` calls the first `__init__` in its MRO: `pkg.C.__init__` if a
  package class defines it; if the first `__init__` is outside the package it is named through the
  nearest outside base (`<builtin>.Exception.__init__`, `collections.UserDict.__init__`); if it is
  `object.__init__` there is no edge. A package `__new__` is also a callee. Calling a builtin or
  external class gives an edge to the class itself (`<builtin>.ValueError`, `threading.Thread`).
- Implicit calls of package functions are edges: `__init__` on instantiation, `__enter__`/`__exit__`
  in `with`, `__iter__`/`__next__` in `for`, operators (`__add__`, `__eq__`, ...), `x[k]`
  (`__getitem__`), properties (the getter/setter function), `__bool__`/`__len__` in truth tests,
  `__str__`/`__format__` in f-strings, decorators (applying `@d` calls `d`).
  Implicit calls of builtin/library code are NOT edges (a `with open(...)` adds no `__enter__` edge).
- Callbacks: a package function that builtin/library code calls belongs to the caller whose call
  made it run (`list(map(f, xs))` in `main` gives `main -> main.f`; `sorted(xs, key=k)` gives `-> k`;
  `Thread(target=t).start()` gives `-> t` in the scope that calls `start()`). A lazy `map` object
  that is returned unconsumed does not call `f` in this scope.
- Calling a generator or coroutine function is an edge from the calling scope (even if never iterated).
- super(): `super().m()` calls the next `m` in the MRO after the current class.
- Imports add no edges; module top-level code is the module node.
Names of callees outside the package:
- builtins: `<builtin>.len`, `<builtin>.print`, `<builtin>.isinstance`; methods of builtin types by
  the receiver's type: `<builtin>.str.join`, `<builtin>.list.append`, `<builtin>.dict.get`.
- library functions by the import path the code uses: `os.path.join`, `re.compile`, `json.dumps`;
  methods by the public class of the receiver: `re.Pattern.match`, `logging.Logger.info`,
  `threading.Thread.start`, `io.TextIOWrapper.write` (files from `open()` in text mode).
- a module that is not installed/unknown: by the access path, e.g. `ext.Cls.fun`; calling `ext.f()`
  returns an instance of the stub, so `ext.client().get()` calls `ext.client` and `ext.client.get`.
List every possible callee (the analysis is a may-analysis), but do not guess: a callee needs a
reason in the code (a binding, an assignment, an argument passed, a documented type, a class hierarchy).
"""

SITE_SCHEMA = {
    "type": "object",
    "properties": {
        "sites": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "callees": {"type": "array", "items": {"type": "string"}}},
                "required": ["id", "callees"],
            },
        }
    },
    "required": ["sites"],
}

EDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"caller": {"type": "string"}, "callees": {"type": "array", "items": {"type": "string"}}},
                "required": ["caller", "callees"],
            },
        }
    },
    "required": ["edges"],
}


def llm_only_prompt(program_desc, sources, callers, outline=None):
    """V0: the model reads the source and writes the call graph directly."""
    parts = [
        "# Task\nBuild the static call graph of the Python code below.",
        CONVENTIONS,
    ]
    if outline:
        parts.append("## Definitions of the whole package (for naming callees in other modules)\n" + outline)
    parts.append(f"## Source ({program_desc})\n" + sources)
    parts.append(
        "## Output\nReturn {\"edges\": [{\"caller\": <node>, \"callees\": [<callee>, ...]}, ...]} with one entry "
        "for every caller node below (use an empty list when it calls nothing):\n" + "\n".join(callers)
    )
    return "\n\n".join(parts)


def site_line(s, hints=True, pycg=None):
    head = f"{s.sid} | caller {s.caller} | line {s.line} col {s.col} | {s.kind} | `{s.text}`"
    if not hints:
        return head
    extra = []
    if s.resolved:
        extra.append("symbolic resolution: [" + ", ".join(s.resolved) + "]" + (" (certain)" if s.certain else ""))
    if s.candidates:
        extra.append("package functions with this name: [" + ", ".join(s.candidates) + "]")
    if s.callbacks:
        extra.append("package functions passed as arguments: [" + ", ".join(s.callbacks) + "]")
    if getattr(s, "hooks", None):
        extra.append("package overrides of library classes that this library call may call back: ["
                     + ", ".join(s.hooks) + "]")
    if s.specials and s.kind != "call":
        extra.append("special methods involved: " + ", ".join(s.specials))
    elif s.specials:
        extra.append("this builtin may call special methods: " + ", ".join(s.specials))
    if not extra:
        extra.append("no symbolic information")
    return head + "\n    " + "\n    ".join(extra)


def site_prompt(program_desc, sources, sites, outline, facts="", hints=True, pycg_hints=None):
    """V1/V2/V3: decide the callees of symbolically enumerated call sites."""
    parts = [
        "# Task\nYou are given call sites that a symbolic front-end found in the Python code below. For each site,"
        " decide which functions the site can call when its node runs.",
        CONVENTIONS,
        "## How to use the site information\n"
        "- `symbolic resolution` comes from a flow-insensitive static resolver; it is usually right for plain names"
        " and module attributes (marked certain), but it can miss values and can over-approximate.\n"
        "- `package functions with this name` is a naive name match over the whole package: keep only those that the"
        " receiver can really be (check the types, the class hierarchy, the assignments).\n"
        "- For implicit sites (kind is not call/decorator/raise), answer only package functions that really run;"
        " an empty list is a valid answer.\n"
        "- For `call` and `decorator` sites also add callees outside the package (builtins, standard library,"
        " third-party), named by the conventions above.\n"
        "- Use only package names that appear in the definitions; never invent a package function."
        if hints else
        "## Notes\nFor implicit sites (kind is not call/decorator/raise) answer only package functions that really run."
        " For `call` and `decorator` sites also add callees outside the package, named by the conventions above.",
    ]
    if outline:
        parts.append("## Definitions of the package (symbolic outline)\n" + outline)
    if facts and hints:
        parts.append("## Attribute assignments in the package that matter for these sites (symbolic facts)\n" + facts)
    if pycg_hints:
        parts.append(
            "## A static analyzer (PyCG) reports these callees for the callers of the sites below\n"
            "Treat them as evidence, not as truth: the analyzer can miss callees and can report spurious ones.\n"
            + pycg_hints)
    parts.append(f"## Source ({program_desc}), with line numbers\n" + sources)
    parts.append("## Call sites to decide\n" + "\n".join(site_line(s, hints) for s in sites))
    parts.append("## Output\nReturn {\"sites\": [{\"id\": <site id>, \"callees\": [...]}, ...]} with one entry for every"
                 " site id above.")
    return "\n\n".join(parts)
