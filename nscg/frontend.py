"""Symbolic front-end of NSCG.

It reads a Python program with `ast` (it never imports or runs it) and computes

* the nodes of the call graph, named with the benchmark conventions (modules,
  functions, methods, lambdas `<lambdaN>`; classes and comprehensions are not nodes);
* a definition index (functions, classes with bases / MRO / methods / properties,
  module and function bindings, imports, attribute-assignment facts);
* every call site, explicit (`call`, `decorator`, `raise C`) and implicit (`with`,
  `for`, operators, subscripts, properties, truth tests, f-strings, class creation),
  attributed to the node whose execution makes the call;
* for each site, a *symbolic pre-resolution* (callees derived by a light-weight,
  flow-insensitive value resolver) and *name-based candidates* (every package
  function whose name matches), plus the package functions passed as arguments
  (callbacks). Implicit sites are kept only when some package function can be called.

The output is consumed by `nscg.pipeline`, which asks the LLM to decide each site
and validates the answers symbolically.
"""

from __future__ import annotations

import ast
import builtins
import warnings
from dataclasses import dataclass, field
from pathlib import Path

BUILTIN_NAMES = frozenset(dir(builtins))
MAX_DEPTH = 6

# Builtins that call special methods of their argument (explicit call -> implicit package callees).
BUILTIN_SPECIALS = {
    "len": ["__len__"],
    "str": ["__str__", "__repr__"],
    "repr": ["__repr__"],
    "format": ["__format__", "__str__", "__repr__"],
    "hash": ["__hash__"],
    "bool": ["__bool__", "__len__"],
    "int": ["__int__", "__index__", "__trunc__"],
    "float": ["__float__", "__index__"],
    "complex": ["__complex__", "__float__", "__index__"],
    "bytes": ["__bytes__", "__index__", "__iter__"],
    "abs": ["__abs__"],
    "round": ["__round__"],
    "iter": ["__iter__", "__getitem__"],
    "next": ["__next__"],
    "reversed": ["__reversed__", "__len__", "__getitem__"],
    "dir": ["__dir__"],
    "divmod": ["__divmod__", "__rdivmod__"],
    "pow": ["__pow__", "__rpow__"],
    "list": ["__iter__", "__next__", "__len__", "__getitem__"],
    "tuple": ["__iter__", "__next__", "__len__", "__getitem__"],
    "set": ["__iter__", "__next__", "__hash__", "__eq__"],
    "frozenset": ["__iter__", "__next__", "__hash__", "__eq__"],
    "dict": ["__iter__", "__next__", "keys", "__getitem__", "__hash__", "__eq__"],
    "sorted": ["__iter__", "__next__", "__lt__", "__gt__"],
    "min": ["__iter__", "__next__", "__lt__", "__gt__"],
    "max": ["__iter__", "__next__", "__lt__", "__gt__"],
    "sum": ["__iter__", "__next__", "__add__", "__radd__"],
    "any": ["__iter__", "__next__", "__bool__", "__len__"],
    "all": ["__iter__", "__next__", "__bool__", "__len__"],
    "enumerate": ["__iter__"],
    "zip": ["__iter__"],
    "map": ["__iter__"],
    "filter": ["__iter__"],
    "isinstance": ["__instancecheck__"],
    "issubclass": ["__subclasscheck__"],
    "getattr": ["__getattr__", "__getattribute__"],
    "setattr": ["__setattr__"],
    "delattr": ["__delattr__"],
    "vars": [],
}

BINOP_DUNDERS = {
    ast.Add: ("__add__", "__radd__"), ast.Sub: ("__sub__", "__rsub__"),
    ast.Mult: ("__mul__", "__rmul__"), ast.MatMult: ("__matmul__", "__rmatmul__"),
    ast.Div: ("__truediv__", "__rtruediv__"), ast.FloorDiv: ("__floordiv__", "__rfloordiv__"),
    ast.Mod: ("__mod__", "__rmod__"), ast.Pow: ("__pow__", "__rpow__"),
    ast.LShift: ("__lshift__", "__rlshift__"), ast.RShift: ("__rshift__", "__rrshift__"),
    ast.BitOr: ("__or__", "__ror__"), ast.BitXor: ("__xor__", "__rxor__"),
    ast.BitAnd: ("__and__", "__rand__"),
}
INPLACE = {k: "__i" + v[0][2:] for k, v in BINOP_DUNDERS.items()}
CMP_DUNDERS = {
    ast.Eq: ("__eq__",), ast.NotEq: ("__ne__", "__eq__"), ast.Lt: ("__lt__", "__gt__"),
    ast.LtE: ("__le__", "__ge__"), ast.Gt: ("__gt__", "__lt__"), ast.GtE: ("__ge__", "__le__"),
    ast.In: ("__contains__", "__iter__", "__getitem__"), ast.NotIn: ("__contains__", "__iter__", "__getitem__"),
}
UNARY_DUNDERS = {ast.USub: ("__neg__",), ast.UAdd: ("__pos__",), ast.Invert: ("__invert__",)}
# Iterables whose iteration is builtin by construction (no site).
BUILTIN_ITERABLE_CALLS = {"range", "enumerate", "zip", "reversed", "sorted", "map", "filter", "dir", "vars",
                          "globals", "locals"}


@dataclass
class Func:
    qname: str
    module: str
    kind: str  # module | function | lambda
    node: ast.AST
    cls: str | None
    name: str
    lineno: int
    end_lineno: int
    params: list = field(default_factory=list)
    decorators: list = field(default_factory=list)
    is_async: bool = False
    is_generator: bool = False
    returns: list = field(default_factory=list)  # return-value expressions


@dataclass
class Cls:
    qname: str
    module: str
    node: ast.ClassDef
    owner: str  # the node that runs the class body
    scope: "Scope"
    base_exprs: list
    methods: dict = field(default_factory=dict)  # name -> function qname
    attrs: dict = field(default_factory=dict)  # class-body name -> [expr]
    nested: dict = field(default_factory=dict)  # name -> nested class qname
    properties: dict = field(default_factory=dict)  # name -> {get,set,del: qname}
    metaclass_expr: ast.AST | None = None
    bases: list = field(default_factory=list)  # resolved: ('class', qn) | ('ext', dotted)
    mro: list = field(default_factory=list)


@dataclass
class Site:
    sid: str
    caller: str
    module: str
    line: int
    col: int
    kind: str
    text: str
    resolved: list = field(default_factory=list)  # symbolic callees (internal or external names)
    candidates: list = field(default_factory=list)  # name-based internal candidates
    callbacks: list = field(default_factory=list)  # package functions passed as arguments
    specials: list = field(default_factory=list)  # dunder names this site may invoke
    value_site: bool = False
    certain: bool = False  # the callee is a static path (name / module attribute) with one binding
    hooks: list = field(default_factory=list)  # V2.1: package overrides that library code may call back


class Scope:
    """A naming / binding scope: module, function, lambda or class body."""

    def __init__(self, kind, qname, module, parent, node):
        self.kind, self.qname, self.module, self.parent, self.node = kind, qname, module, parent, node
        self.bindings: dict[str, list] = {}
        self.globals: set = set()
        self.nonlocals: set = set()
        self.cls: str | None = None  # for class scopes: the class qname; for methods: owning class
        self.self_name: str | None = None
        self.first_param_kind: str | None = None  # 'self' | 'cls' | None

    def bind(self, name, value):
        self.bindings.setdefault(name, []).append(value)

    def lookup_chain(self):
        """Scopes visible from here, innermost first; class scopes are skipped except the first."""
        out, s, first = [], self, True
        while s is not None:
            if s.kind != "class" or first:
                out.append(s)
            first = False
            s = s.parent
        return out


def _parse(path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            return ast.parse(Path(path).read_bytes())
        except (SyntaxError, ValueError):
            return None


def unparse(node, limit=120):
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover
        text = type(node).__name__
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


class Program:
    """The analysed program: modules -> nodes, classes, scopes and sites."""

    def __init__(self, files, package_names, library_hooks=False):
        """files: [(module_name, path)]; package_names: top-level names of the analysed package(s).
        library_hooks (V2.1): propose package overrides of library classes at library-method calls."""
        self.package_names = tuple(package_names)
        self.library_hooks = library_hooks
        self.modules: dict[str, dict] = {}
        self.funcs: dict[str, Func] = {}
        self.classes: dict[str, Cls] = {}
        self.module_scopes: dict[str, Scope] = {}
        self.scope_of: dict[int, Scope] = {}  # id(def node) -> its scope
        self.attr_facts: dict[str, list] = {}  # attribute name -> [(expr, Scope)]
        self.sites: list[Site] = []
        self.by_simple_name: dict[str, list] = {}
        self.lambda_names: dict[int, str] = {}
        self.future_annotations: dict[str, bool] = {}
        for name, path in files:
            tree = _parse(path)
            if tree is None:
                continue
            src = Path(path).read_text(errors="replace")
            self.modules[name] = {"path": Path(path), "tree": tree, "lines": src.splitlines()}
        for name in sorted(self.modules):
            self._define_module(name)
        for c in self.classes.values():
            c.bases = [b for e in c.base_exprs for b in self._class_values(e, c.scope)]
        for c in self.classes.values():
            c.mro = self._mro(c.qname, set())
        self.subclasses: dict[str, set] = {q: set() for q in self.classes}
        for q in self.classes:
            for b in self.classes[q].mro[1:]:
                if b[0] == "class" and b[1] in self.subclasses:
                    self.subclasses[b[1]].add(q)
        for f in self.funcs.values():
            if f.kind != "module":
                self.by_simple_name.setdefault(f.name, []).append(f.qname)
        self._sid = 0
        for name in sorted(self.modules):
            self._collect_sites(name)
        self._param_flows()

    # ------------------------------------------------------------------ definitions
    def in_package(self, dotted):
        return any(dotted == p or dotted.startswith(p + ".") for p in self.package_names)

    def _define_module(self, mod):
        tree = self.modules[mod]["tree"]
        self.future_annotations[mod] = any(
            isinstance(s, ast.ImportFrom) and s.module == "__future__" and any(a.name == "annotations" for a in s.names)
            for s in tree.body
        )
        scope = Scope("module", mod, mod, None, tree)
        self.module_scopes[mod] = scope
        self.funcs[mod] = Func(mod, mod, "module", tree, None, mod.split(".")[-1], 1, len(self.modules[mod]["lines"]))
        self._define_body(tree.body, scope, owner=mod)

    def _number_lambdas(self, nodes, prefix):
        found = []

        def visit(n):
            if isinstance(n, ast.Lambda):
                found.append(n)
                for d in n.args.defaults + [d for d in n.args.kw_defaults if d is not None]:
                    visit(d)
                return
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for d in n.decorator_list + n.args.defaults + [d for d in n.args.kw_defaults if d is not None]:
                    visit(d)
                return
            if isinstance(n, ast.ClassDef):
                for d in n.decorator_list + n.bases + [k.value for k in n.keywords]:
                    visit(d)
                return
            for c in ast.iter_child_nodes(n):
                visit(c)

        for n in nodes:
            visit(n)
        found.sort(key=lambda n: (n.lineno, n.col_offset))
        for i, lam in enumerate(found, 1):
            self.lambda_names[id(lam)] = f"{prefix}.<lambda{i}>"
        return found

    def _define_body(self, body, scope, owner):
        """Define everything evaluated in `scope` (statements or one expression)."""
        nodes = body if isinstance(body, list) else [body]
        lambdas = self._number_lambdas(nodes, scope.qname)
        for lam in lambdas:
            self._define_lambda(lam, scope)
        for n in nodes:
            self._define_stmt(n, scope, owner)

    def _define_lambda(self, lam, scope):
        qn = self.lambda_names[id(lam)]
        f = Func(qn, scope.module, "lambda", lam, None, "<lambda>", lam.lineno, getattr(lam, "end_lineno", lam.lineno))
        f.params = [a.arg for a in lam.args.posonlyargs + lam.args.args + lam.args.kwonlyargs]
        f.returns = [lam.body]
        self.funcs[qn] = f
        ls = Scope("function", qn, scope.module, scope, lam)
        self.scope_of[id(lam)] = ls
        for p in f.params + [a.arg for a in (lam.args.vararg, lam.args.kwarg) if a]:
            ls.bind(p, ("param", qn, p))
        self._define_body(lam.body, ls, owner=qn)

    def _define_stmt(self, n, scope, owner):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._define_function(n, scope, owner)
            return
        if isinstance(n, ast.ClassDef):
            self._define_class(n, scope, owner)
            return
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            self._bind_import(n, scope)
            return
        if isinstance(n, ast.Global):
            scope.globals.update(n.names)
        elif isinstance(n, ast.Nonlocal):
            scope.nonlocals.update(n.names)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                self._bind_target(t, n.value, scope)
        elif isinstance(n, ast.AnnAssign) and n.value is not None:
            self._bind_target(n.target, n.value, scope)
        elif isinstance(n, ast.AugAssign):
            self._bind_target(n.target, None, scope)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            self._bind_target(n.target, None, scope)
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            for item in n.items:
                if item.optional_vars is not None:
                    self._bind_target(item.optional_vars, ("enter", item.context_expr), scope)
        elif isinstance(n, ast.NamedExpr):
            self._bind_target(n.target, n.value, scope)
        elif isinstance(n, ast.Return) and n.value is not None and scope.qname in self.funcs:
            self.funcs[scope.qname].returns.append(n.value)
        elif isinstance(n, (ast.Yield, ast.YieldFrom)) and scope.qname in self.funcs:
            self.funcs[scope.qname].is_generator = True
        elif isinstance(n, ast.ExceptHandler) and n.name:
            scope.bind(n.name, ("unknown", "exception"))
        # Recurse into compound statements / expressions evaluated in the same scope.
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.Lambda,)):
                continue  # defined by _number_lambdas/_define_lambda
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self._define_stmt(c, scope, owner)
            elif isinstance(c, (ast.stmt, ast.expr, ast.excepthandler, ast.match_case, ast.comprehension, ast.withitem)):
                self._define_stmt(c, scope, owner)

    def _define_function(self, n, scope, owner):
        qn = f"{scope.qname}.{n.name}"
        cls = scope.cls if scope.kind == "class" else None
        f = self.funcs.get(qn) or Func(qn, scope.module, "function", n, cls, n.name, n.lineno, n.end_lineno)
        f.node, f.lineno, f.end_lineno = n, min(f.lineno, n.lineno), max(f.end_lineno, n.end_lineno)
        f.is_async = isinstance(n, ast.AsyncFunctionDef)
        f.params = [a.arg for a in n.args.posonlyargs + n.args.args + n.args.kwonlyargs]
        f.decorators = [unparse(d, 60) for d in n.decorator_list]
        self.funcs[qn] = f
        fs = Scope("function", qn, scope.module, scope, n)
        self.scope_of[id(n)] = fs
        decos = [unparse(d) for d in n.decorator_list]
        if cls:
            fs.cls = cls
            if f.params and "staticmethod" not in decos:
                fs.self_name = f.params[0]
                fs.first_param_kind = "cls" if ("classmethod" in decos or n.name in ("__new__", "__init_subclass__", "__class_getitem__")) else "self"
        for p in f.params + [a.arg for a in (n.args.vararg, n.args.kwarg) if a]:
            fs.bind(p, ("param", qn, p))
        # Binding in the enclosing scope (decorated functions stay bound to their def, with a marker).
        value = ("def", qn) if not n.decorator_list else ("decorated", qn, n.decorator_list, scope)
        if scope.kind == "class":
            c = self.classes[scope.cls]
            prop = None
            for d in n.decorator_list:
                t = unparse(d)
                if t in ("property", "functools.cached_property", "cached_property"):
                    prop = (n.name, "get")
                elif isinstance(d, ast.Attribute) and d.attr in ("setter", "getter", "deleter"):
                    prop = (unparse(d.value), {"setter": "set", "getter": "get", "deleter": "del"}[d.attr])
            if prop:
                c.properties.setdefault(prop[0], {})[prop[1]] = qn
            c.methods.setdefault(n.name, qn)
            scope.bind(n.name, value)
        else:
            scope.bind(n.name, value)
        self._define_body(n.body, fs, owner=qn)

    def _define_class(self, n, scope, owner):
        qn = f"{scope.qname}.{n.name}"
        cs = Scope("class", qn, scope.module, scope, n)
        cs.cls = qn
        meta = next((k.value for k in n.keywords if k.arg == "metaclass"), None)
        c = Cls(qn, scope.module, n, owner, scope, list(n.bases), metaclass_expr=meta)
        self.classes[qn] = c
        self.scope_of[id(n)] = cs
        scope.bind(n.name, ("class", qn))
        if scope.kind == "class":
            self.classes[scope.cls].nested[n.name] = qn
        self._define_body(n.body, cs, owner=owner)
        for name, vals in cs.bindings.items():
            for v in vals:
                if v and v[0] == "assign":
                    c.attrs.setdefault(name, []).append(v[1])
                    # property(fget, fset) in a class body
                    if isinstance(v[1], ast.Call) and unparse(v[1].func) == "property":
                        roles = ["get", "set", "del"]
                        args = list(v[1].args) + [k.value for k in v[1].keywords if k.arg in ("fget", "fset", "fdel")]
                        for i, a in enumerate(args[:3]):
                            if isinstance(a, ast.Name) and a.id in cs.bindings:
                                for bv in cs.bindings[a.id]:
                                    if bv[0] in ("def", "decorated"):
                                        c.properties.setdefault(name, {})[roles[i]] = bv[1]
                            elif isinstance(a, ast.Lambda) and id(a) in self.lambda_names:
                                c.properties.setdefault(name, {})[roles[i]] = self.lambda_names[id(a)]

    def _bind_import(self, n, scope):
        mod = scope.module
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.asname:
                    scope.bind(a.asname, ("module", a.name))
                else:
                    scope.bind(a.name.split(".")[0], ("module", a.name.split(".")[0]))
        else:
            base = n.module or ""
            if n.level:
                is_pkg = self.modules.get(mod, {}).get("path", Path("x.py")).name == "__init__.py"
                parts = mod.split(".")
                up = n.level - (1 if is_pkg else 0)
                parts = parts[: len(parts) - up] if up > 0 else parts
                base = ".".join(parts + ([n.module] if n.module else []))
            for a in n.names:
                if a.name == "*":
                    scope.bind("*", ("star", base))
                    continue
                scope.bind(a.asname or a.name, ("from", base, a.name))

    def _bind_target(self, t, value, scope):
        if isinstance(t, ast.Name):
            if value is None:
                scope.bind(t.id, ("unknown", "rebound"))
            elif isinstance(value, tuple):
                scope.bind(t.id, value)
            else:
                scope.bind(t.id, ("assign", value, scope))
        elif isinstance(t, (ast.Tuple, ast.List)):
            vals = value.elts if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(t.elts) else None
            for i, e in enumerate(t.elts):
                self._bind_target(e, vals[i] if vals else None, scope)
        elif isinstance(t, ast.Attribute) and value is not None and not isinstance(value, tuple):
            self.attr_facts.setdefault(t.attr, []).append((value, scope, unparse(t.value, 40)))
        elif isinstance(t, ast.Starred):
            self._bind_target(t.value, None, scope)

    # ------------------------------------------------------------------ resolution
    def _scope_for_node(self, qname):
        f = self.funcs.get(qname)
        if f is None:
            return None
        if f.kind == "module":
            return self.module_scopes[qname]
        return self.scope_of.get(id(f.node))

    def module_member(self, mod, name, depth):
        """Values of `mod.name` for a package module `mod`."""
        sub = f"{mod}.{name}"
        out = []
        if mod in self.module_scopes:
            s = self.module_scopes[mod]
            if name in s.bindings:
                out += self._binding_values(s.bindings[name], s, depth)
            elif "*" in s.bindings:
                for b in s.bindings["*"]:
                    out += self.module_member(b[1], name, depth - 1) if b[1] in self.module_scopes else [("ext", f"{b[1]}.{name}")]
        if sub in self.modules:
            out.append(("module", sub))
        return out

    def _binding_values(self, bindings, scope, depth):
        out = []
        for b in bindings:
            k = b[0]
            if k == "def":
                out.append(("func", b[1]))
            elif k == "decorated":
                out.append(("decorated", b[1], b[2], b[3]))
            elif k == "class":
                out.append(("class", b[1]))
            elif k == "module":
                out.append(("module", b[1]) if b[1] in self.modules else ("ext", b[1]))
            elif k == "from":
                base, name = b[1], b[2]
                if base in self.modules or f"{base}.{name}" in self.modules:
                    out += self.module_member(base, name, depth - 1) if depth > 0 else []
                elif self.in_package(base):
                    out.append(("unknown", f"{base}.{name}"))
                else:
                    out.append(("ext", f"{base}.{name}"))
            elif k == "assign" and depth > 0:
                out += self.resolve(b[1], b[2], depth - 1)
            elif k == "enter" and depth > 0:
                for v in self.resolve(b[1], scope, depth - 1):
                    if v[0] == "inst":
                        for m in self.lookup_attr(v[1], "__enter__"):
                            if m[0] == "func":
                                f = self.funcs[m[1]]
                                fs = self._scope_for_node(f.qname)
                                for r in f.returns:
                                    out += self.resolve(r, fs, depth - 2) if fs else []
                    elif v[0] in ("ext", "extinst"):
                        out.append(("extinst", v[1]))
            elif k == "param":
                fq, p = b[1], b[2]
                fs = self._scope_for_node(fq)
                if fs is not None and fs.cls and fs.self_name == p:
                    out.append(("inst" if fs.first_param_kind == "self" else "class", fs.cls))
                else:
                    out.append(("param", fq, p))
            else:
                out.append(("unknown", str(k)))
        return out

    def lookup_name(self, name, scope, depth=MAX_DEPTH):
        for s in scope.lookup_chain():
            if name in s.globals:
                ms = self.module_scopes[s.module]
                return self._binding_values(ms.bindings.get(name, []), ms, depth) if name in ms.bindings else []
            if name in s.bindings:
                return self._binding_values(s.bindings[name], s, depth)
            if s.kind == "module" and "*" in s.bindings:
                for b in s.bindings["*"]:
                    if b[1] in self.module_scopes:
                        vals = self.module_member(b[1], name, depth - 1)
                        if vals:
                            return vals
        if name in BUILTIN_NAMES:
            return [("ext", f"<builtin>.{name}")]
        return []

    def lookup_attr(self, cls_qname, attr):
        """Look `attr` up through the MRO of a package class -> values."""
        c = self.classes.get(cls_qname)
        if c is None:
            return []
        for kind, q in c.mro:
            if kind == "ext":
                if q in ("<builtin>.object", "object"):
                    return []
                return [("ext", f"{q}.{attr}")]
            k = self.classes[q]
            if attr in k.methods:
                return [("func", k.methods[attr])]
            if attr in k.nested:
                return [("class", k.nested[attr])]
            if attr in k.attrs:
                out = []
                for e in k.attrs[attr]:
                    out += self.resolve(e, k.scope, 2)
                return out or [("unknown", f"{q}.{attr}")]
        return []

    def hook_methods(self, libs):
        """Methods of package classes that derive from a class of one of the libraries `libs`:
        the code of those libraries can call them back (template methods, hooks)."""
        if not hasattr(self, "_hooks"):
            self._hooks = {}
        key = tuple(sorted(libs))
        if key not in self._hooks:
            out = []
            for q, c in sorted(self.classes.items()):
                ext = [b[1] for b in c.mro if b[0] == "ext" and b[1].split(".")[0] in libs]
                if not ext:
                    continue
                out += [m for name, m in c.methods.items() if name not in ("__init__", "__new__", "__repr__")]
            self._hooks[key] = out
        return self._hooks[key]

    def overrides(self, cls_qname, attr):
        """Methods named `attr` in package subclasses of `cls_qname` (possible receivers)."""
        out = []
        for sub in sorted(self.subclasses.get(cls_qname, ())):
            k = self.classes[sub]
            if attr in k.methods:
                out.append(k.methods[attr])
        return out

    def _class_values(self, expr, scope):
        out = []
        if isinstance(expr, ast.Subscript):
            expr = expr.value
        for v in self.resolve(expr, scope, 4):
            if v[0] == "class":
                out.append(("class", v[1]))
            elif v[0] == "ext":
                out.append(("ext", v[1]))
        if not out:
            out.append(("ext", unparse(expr, 60)))
        return out[:1]

    def _mro(self, qn, seen):
        if qn in seen:
            return [("class", qn)]
        seen = seen | {qn}
        c = self.classes[qn]
        seqs = []
        for b in c.bases:
            seqs.append(self._mro(b[1], seen) if b[0] == "class" else [b])
        seqs.append(list(c.bases))
        out = [("class", qn)]
        seqs = [list(s) for s in seqs if s]
        while seqs:
            for s in seqs:
                head = s[0]
                if not any(head in t[1:] for t in seqs):
                    break
            else:
                head = seqs[0][0]
            out.append(head)
            seqs = [[x for x in s if x != head] for s in seqs]
            seqs = [s for s in seqs if s]
        dedup = []
        for x in out:
            if x not in dedup:
                dedup.append(x)
        return dedup

    def resolve(self, expr, scope, depth=MAX_DEPTH):
        """Flow-insensitive value resolution of an expression (a set of abstract values)."""
        if depth <= 0 or expr is None or scope is None:
            return []
        if isinstance(expr, ast.Name):
            return self.lookup_name(expr.id, scope, depth)
        if isinstance(expr, ast.Attribute):
            out = []
            for v in self.resolve(expr.value, scope, depth - 1):
                out += self._attr_of(v, expr.attr, depth)
            return out
        if isinstance(expr, ast.Call):
            f = expr.func
            if isinstance(f, ast.Name) and f.id == "super" and scope.lookup_chain():
                cls = self._enclosing_class(scope)
                return [("super", cls)] if cls else []
            out = []
            for v in self.resolve(f, scope, depth - 1):
                out += self._call_result(v, depth)
            return out
        if isinstance(expr, ast.Lambda) and id(expr) in self.lambda_names:
            return [("func", self.lambda_names[id(expr)])]
        if isinstance(expr, (ast.IfExp,)):
            return self.resolve(expr.body, scope, depth - 1) + self.resolve(expr.orelse, scope, depth - 1)
        if isinstance(expr, ast.BoolOp):
            out = []
            for e in expr.values:
                out += self.resolve(e, scope, depth - 1)
            return out
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            return [("extinst", "<builtin>.str")]
        if isinstance(expr, ast.JoinedStr):
            return [("extinst", "<builtin>.str")]
        if isinstance(expr, (ast.List, ast.ListComp)):
            return [("extinst", "<builtin>.list")]
        if isinstance(expr, (ast.Dict, ast.DictComp)):
            return [("extinst", "<builtin>.dict")]
        if isinstance(expr, (ast.Set, ast.SetComp)):
            return [("extinst", "<builtin>.set")]
        if isinstance(expr, ast.Tuple):
            return [("extinst", "<builtin>.tuple")]
        return []

    def _enclosing_class(self, scope):
        s = scope
        while s is not None:
            if s.kind == "function" and s.cls:
                return s.cls
            s = s.parent
        return None

    def _attr_of(self, v, attr, depth):
        k = v[0]
        if k == "module":
            if v[1] in self.modules:
                return self.module_member(v[1], attr, depth - 1)
            return [("ext", f"{v[1]}.{attr}")]
        if k in ("class", "inst"):
            vals = self.lookup_attr(v[1], attr)
            if k == "inst":
                facts = [f for f in self.attr_facts.get(attr, []) if self._enclosing_class(f[1]) in (
                    [v[1]] + [b[1] for b in self.classes[v[1]].mro if b[0] == "class"] + sorted(self.subclasses.get(v[1], ())))]
                for e, s, _ in facts[:6]:
                    vals = vals + self.resolve(e, s, min(depth - 1, 3))
                return [("bound", x[1], v[1]) if x[0] == "func" else x for x in vals]
            return vals
        if k == "super":
            c = self.classes.get(v[1])
            if not c:
                return []
            for kind, q in c.mro[1:]:
                if kind == "ext":
                    return [("ext", f"{q}.{attr}")] if q not in ("object", "<builtin>.object") else []
                kk = self.classes[q]
                if attr in kk.methods:
                    return [("bound", kk.methods[attr], v[1])]
            return []
        if k == "ext":
            return [("ext", f"{v[1]}.{attr}")]
        if k == "extinst":
            return [("ext", f"{v[1]}.{attr}")]
        return []

    def _call_result(self, v, depth):
        k = v[0]
        if k == "class":
            return [("inst", v[1])]
        if k in ("func", "bound") and depth > 1:
            f = self.funcs.get(v[1])
            if f is None or f.is_generator or f.is_async:
                return []
            fs = self._scope_for_node(f.qname)
            out = []
            for r in f.returns[:4]:
                out += self.resolve(r, fs, min(depth - 1, 3))
            return out
        if k == "ext":
            return [("extinst", v[1])]
        if k == "extinst":
            return [("extinst", v[1])]
        return []

    # ------------------------------------------------------------------ call targets
    def constructor_targets(self, cls_qname):
        c = self.classes.get(cls_qname)
        if c is None:
            return []
        out = []
        for kind, q in c.mro:
            if kind == "ext":
                if q not in ("object", "<builtin>.object") and not q.endswith(".Protocol") and q not in (
                        "typing.NamedTuple", "typing.Generic", "abc.ABC"):
                    out.append(f"{q}.__init__")
                break
            if "__init__" in self.classes[q].methods:
                out.append(self.classes[q].methods["__init__"])
                break
        for kind, q in c.mro:
            if kind == "class" and "__new__" in self.classes[q].methods:
                out.append(self.classes[q].methods["__new__"])
                break
        if c.metaclass_expr is not None:
            for mv in self.resolve(c.metaclass_expr, c.scope, 3):
                if mv[0] == "class":
                    out += [m[1] for m in self.lookup_attr(mv[1], "__call__") if m[0] == "func"]
        return out

    def targets_of(self, v):
        k = v[0]
        if k in ("func", "bound"):
            return [v[1]]
        if k == "decorated":
            return [v[1]]  # the decorated def; the LLM decides about wrappers
        if k == "class":
            return self.constructor_targets(v[1])
        if k == "inst":
            return [m[1] if m[0] == "func" else m[1] for m in self.lookup_attr(v[1], "__call__") if m[0] in ("func", "ext")]
        if k == "ext":
            return [v[1]]
        return []

    # ------------------------------------------------------------------ sites
    def _new_site(self, caller, mod, node, kind, text, **kw):
        self._sid += 1
        line = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0) + 1
        s = Site(f"s{self._sid}", caller, mod, line, col, kind, text, **kw)
        self.sites.append(s)
        return s

    def _collect_sites(self, mod):
        tree = self.modules[mod]["tree"]
        self._walk(tree.body, self.module_scopes[mod], caller=mod)

    def _walk(self, nodes, scope, caller):
        for n in nodes if isinstance(nodes, list) else [nodes]:
            self._visit(n, scope, caller)

    def _visit(self, n, scope, caller):
        mod = scope.module
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.decorator_list:
                self._visit(d, scope, caller)
                self._decorator_site(d, scope, caller)
            for d in n.args.defaults + [d for d in n.args.kw_defaults if d is not None]:
                self._visit(d, scope, caller)
            if not self.future_annotations.get(mod):
                for a in n.args.posonlyargs + n.args.args + n.args.kwonlyargs:
                    if a.annotation is not None:
                        self._visit(a.annotation, scope, caller)
            fs = self.scope_of[id(n)]
            self._walk(n.body, fs, caller=fs.qname)
            return
        if isinstance(n, ast.Lambda):
            for d in n.args.defaults + [d for d in n.args.kw_defaults if d is not None]:
                self._visit(d, scope, caller)
            ls = self.scope_of.get(id(n))
            if ls is not None:
                self._visit(n.body, ls, caller=ls.qname)
            return
        if isinstance(n, ast.ClassDef):
            for d in n.decorator_list:
                self._visit(d, scope, caller)
                self._decorator_site(d, scope, caller)
            for b in n.bases + [k.value for k in n.keywords]:
                self._visit(b, scope, caller)
            cs = self.scope_of[id(n)]
            self._class_site(n, cs, caller)
            self._walk(n.body, cs, caller=caller)
            return
        if isinstance(n, ast.Call):
            self._call_site(n, scope, caller)
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            names = ("__aenter__", "__aexit__") if isinstance(n, ast.AsyncWith) else ("__enter__", "__exit__")
            for item in n.items:
                self._implicit(item.context_expr, scope, caller, "with", names)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            names = ("__aiter__", "__anext__") if isinstance(n, ast.AsyncFor) else ("__iter__", "__next__", "__getitem__")
            self._iter_site(n.iter, scope, caller, names)
        elif isinstance(n, ast.comprehension):
            names = ("__aiter__", "__anext__") if n.is_async else ("__iter__", "__next__", "__getitem__")
            self._iter_site(n.iter, scope, caller, names)
        elif isinstance(n, ast.YieldFrom):
            self._iter_site(n.value, scope, caller, ("__iter__", "__next__"))
        elif isinstance(n, ast.Await):
            self._implicit(n.value, scope, caller, "await", ("__await__",), anchor=n)
        elif isinstance(n, ast.BinOp) and type(n.op) in BINOP_DUNDERS:
            if not (isinstance(n.left, ast.Constant) and isinstance(n.right, ast.Constant)):
                self._implicit(n.left, scope, caller, "op", BINOP_DUNDERS[type(n.op)], anchor=n,
                               text=unparse(n))
        elif isinstance(n, ast.AugAssign) and type(n.op) in BINOP_DUNDERS:
            self._implicit(n.target, scope, caller, "op", (INPLACE[type(n.op)],) + BINOP_DUNDERS[type(n.op)],
                           anchor=n, text=unparse(n))
        elif isinstance(n, ast.UnaryOp) and type(n.op) in UNARY_DUNDERS:
            self._implicit(n.operand, scope, caller, "op", UNARY_DUNDERS[type(n.op)], anchor=n, text=unparse(n))
        elif isinstance(n, ast.Compare):
            for op, right in zip(n.ops, n.comparators):
                if type(op) in CMP_DUNDERS:
                    self._implicit(n.left if not isinstance(op, (ast.In, ast.NotIn)) else right, scope, caller, "op",
                                   CMP_DUNDERS[type(op)], anchor=n, text=unparse(n))
        elif isinstance(n, ast.Subscript):
            names = {ast.Load: ("__getitem__", "__missing__", "__class_getitem__"), ast.Store: ("__setitem__",),
                     ast.Del: ("__delitem__",)}[type(n.ctx)]
            self._implicit(n.value, scope, caller, "getitem" if names[0] == "__getitem__" else names[0].strip("_"),
                           names, anchor=n, text=unparse(n))
        elif isinstance(n, ast.Attribute):
            self._property_site(n, scope, caller)
        elif isinstance(n, (ast.If, ast.While, ast.IfExp, ast.Assert)):
            self._truth_site(n.test, scope, caller)
        elif isinstance(n, ast.BoolOp):
            for v in n.values:
                self._truth_site(v, scope, caller)
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            self._truth_site(n.operand, scope, caller)
        elif isinstance(n, ast.FormattedValue):
            names = ("__repr__",) if n.conversion == ord("r") else ("__format__", "__str__", "__repr__")
            self._implicit(n.value, scope, caller, "format", names, anchor=n.value, text="{" + unparse(n.value) + "}")
        elif isinstance(n, ast.Raise) and n.exc is not None and not isinstance(n.exc, ast.Call):
            self._raise_site(n, scope, caller)
        elif isinstance(n, ast.Starred) and isinstance(getattr(n, "ctx", None), ast.Load):
            self._iter_site(n.value, scope, caller, ("__iter__", "__next__"))
        for c in ast.iter_child_nodes(n):
            self._visit(c, scope, caller)

    # -- explicit sites
    def _call_site(self, n, scope, caller):
        f = n.func
        text = unparse(n)
        values = self.resolve(f, scope)
        resolved = []
        for v in values:
            resolved += self.targets_of(v)
        # `super().__init__()` etc.: already handled through ("super", cls) in resolve.
        name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
        cands = []
        if name:
            cands = [q for q in self.by_simple_name.get(name, []) if q not in resolved]
            # constructors of package classes with this name
            for q, c in self.classes.items():
                if q.split(".")[-1] == name:
                    cands += [t for t in self.constructor_targets(q) if t in self.funcs and t not in resolved]
            # self.m(): receivers include package subclasses
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                for v in self.resolve(f.value, scope, 2):
                    if v[0] in ("inst", "class"):
                        cands += [o for o in self.overrides(v[1], name) if o not in resolved]
        value_site = bool(name) and (
            any(v[0] in ("param", "unknown") for v in values) or not values or name in self.attr_facts)
        # Value sites: what flows into an attribute of this name.
        if isinstance(f, ast.Attribute) and name in self.attr_facts:
            for e, s, _ in self.attr_facts[name][:8]:
                for v in self.resolve(e, s, 3):
                    for t in self.targets_of(v):
                        if t in self.funcs and t not in resolved and t not in cands:
                            cands.append(t)
        callbacks = []
        for a in list(n.args) + [k.value for k in n.keywords]:
            if isinstance(a, ast.Starred):
                a = a.value
            for v in self.resolve(a, scope, 3):
                if v[0] in ("func", "bound", "decorated") and v[1] not in callbacks:
                    callbacks.append(v[1])
                elif v[0] == "class":
                    callbacks += [t for t in self.constructor_targets(v[1]) if t not in callbacks]
        specials = []
        if isinstance(f, ast.Name) and f.id in BUILTIN_SPECIALS and any(r == f"<builtin>.{f.id}" for r in resolved):
            specials = BUILTIN_SPECIALS[f.id]
        certain = (len(values) == 1 and values[0][0] in ("func", "class", "ext") and self._static_path(f, scope)
                   and len(_dedup(resolved)) == 1)
        site = self._new_site(caller, scope.module, n, "call", text, resolved=_dedup(resolved),
                              candidates=_dedup(cands)[:40], callbacks=callbacks[:20], value_site=value_site,
                              certain=certain)
        if self.library_hooks and isinstance(f, ast.Attribute):
            libs = {r.split(".")[0] for r in resolved if not self.in_package(r) and not r.startswith("<builtin>")}
            recv = self.resolve(f.value, scope, 3) if libs else []
            if libs and any(v[0] in ("inst", "class", "super") for v in recv):
                site.hooks = [h for h in self.hook_methods(libs) if h not in site.resolved and h not in site.candidates][:60]
        if specials:
            site.specials = list(specials)
            site.candidates = _dedup(site.candidates + [q for s in specials for q in self.by_simple_name.get(s, [])])[:40]
        for kw in n.keywords:
            if kw.arg is None:  # **mapping
                self._implicit(kw.value, scope, caller, "mapping", ("keys", "__getitem__"))

    def _static_path(self, expr, scope):
        """A name bound once (def / class / import / builtin), or an attribute chain on a module."""
        if isinstance(expr, ast.Name):
            for s in scope.lookup_chain():
                if expr.id in s.globals:
                    s = self.module_scopes[s.module]
                if expr.id in s.bindings:
                    bs = s.bindings[expr.id]
                    return len(bs) == 1 and bs[0][0] in ("def", "class", "module", "from")
            return expr.id in BUILTIN_NAMES
        if isinstance(expr, ast.Attribute):
            base = self.resolve(expr.value, scope, 3)
            return len(base) == 1 and base[0][0] == "module" and self._static_path(expr.value, scope) \
                if isinstance(expr.value, (ast.Name, ast.Attribute)) else False
        return False

    def _decorator_site(self, d, scope, caller):
        if isinstance(d, ast.Call):
            return  # the call itself is a call site; applying its result is another call
        values = self.resolve(d, scope)
        resolved = []
        for v in values:
            resolved += self.targets_of(v)
        name = d.id if isinstance(d, ast.Name) else d.attr if isinstance(d, ast.Attribute) else None
        cands = [q for q in self.by_simple_name.get(name, []) if q not in resolved] if name else []
        self._new_site(caller, scope.module, d, "decorator", "@" + unparse(d), resolved=_dedup(resolved),
                       candidates=cands[:40])

    def _decorator_result_site(self, d, scope, caller):  # pragma: no cover - folded into the LLM's decision
        pass

    def _raise_site(self, n, scope, caller):
        values = self.resolve(n.exc, scope)
        resolved = []
        for v in values:
            if v[0] == "class":
                resolved += [t for t in self.constructor_targets(v[1]) if t in self.funcs]
        name = n.exc.id if isinstance(n.exc, ast.Name) else n.exc.attr if isinstance(n.exc, ast.Attribute) else None
        cands = []
        if name:
            for q in self.classes:
                if q.split(".")[-1] == name:
                    cands += [t for t in self.constructor_targets(q) if t in self.funcs and t not in resolved]
        if resolved or cands:
            self._new_site(caller, scope.module, n.exc, "raise", "raise " + unparse(n.exc), resolved=_dedup(resolved),
                           candidates=_dedup(cands))

    def _class_site(self, n, cs, caller):
        c = self.classes[cs.qname]
        resolved = []
        for kind, q in c.mro[1:]:
            if kind == "class" and "__init_subclass__" in self.classes[q].methods:
                resolved.append(self.classes[q].methods["__init_subclass__"])
                break
        if c.metaclass_expr is not None:
            for mv in self.resolve(c.metaclass_expr, c.scope, 3):
                if mv[0] == "class":
                    for m in ("__prepare__", "__new__", "__init__"):
                        resolved += [x[1] for x in self.lookup_attr(mv[1], m) if x[0] == "func"]
        cands = [q for q in self.by_simple_name.get("__set_name__", [])]
        if resolved or cands:
            self._new_site(caller, cs.module, n, "class", f"class {n.name}({', '.join(unparse(b, 40) for b in n.bases)})",
                           resolved=_dedup(resolved), candidates=_dedup(cands))

    # -- implicit sites
    def _receiver_methods(self, expr, scope, names):
        """Symbolic resolution of an implicit special-method call on `expr`."""
        out = []
        for v in self.resolve(expr, scope, 4):
            if v[0] == "inst":
                for nm in names:
                    out += [m[1] for m in self.lookup_attr(v[1], nm) if m[0] == "func"]
                    out += self.overrides(v[1], nm)
            elif v[0] == "class" and "__class_getitem__" in names:
                out += [m[1] for m in self.lookup_attr(v[1], "__class_getitem__") if m[0] == "func"]
        return _dedup(out)

    def _implicit(self, expr, scope, caller, kind, names, anchor=None, text=None):
        resolved = self._receiver_methods(expr, scope, names)
        cands = []
        for nm in names:
            cands += [q for q in self.by_simple_name.get(nm, []) if q not in resolved]
        if not resolved and not cands:
            return
        self._new_site(caller, scope.module, anchor or expr, kind, text or unparse(expr), resolved=resolved,
                       candidates=_dedup(cands)[:40], specials=list(names))

    def _iter_site(self, expr, scope, caller, names):
        if isinstance(expr, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp,
                             ast.GeneratorExp, ast.Constant, ast.JoinedStr)):
            return
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in BUILTIN_ITERABLE_CALLS:
            return
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr in (
                "items", "keys", "values", "split", "splitlines", "most_common"):
            return
        self._implicit(expr, scope, caller, "iter", names)

    def _truth_site(self, test, scope, caller):
        if isinstance(test, (ast.Compare, ast.Constant, ast.BoolOp)) or (
                isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not)):
            return
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id in (
                "isinstance", "issubclass", "callable", "hasattr", "bool", "len", "any", "all"):
            return
        self._implicit(test, scope, caller, "truth", ("__bool__", "__len__"))

    def _property_site(self, n, scope, caller):
        props = []
        role = {ast.Load: "get", ast.Store: "set", ast.Del: "del"}[type(n.ctx)]
        for q, c in self.classes.items():
            if n.attr in c.properties and role in c.properties[n.attr]:
                props.append(c.properties[n.attr][role])
        if not props:
            return
        resolved = []
        for v in self.resolve(n.value, scope, 3):
            if v[0] == "inst":
                for kind, q in self.classes[v[1]].mro:
                    if kind == "class" and n.attr in self.classes[q].properties:
                        r = self.classes[q].properties[n.attr].get(role)
                        if r:
                            resolved.append(r)
                        break
        self._new_site(caller, scope.module, n, "getattr" if role == "get" else role + "attr", unparse(n),
                       resolved=_dedup(resolved), candidates=[p for p in _dedup(props) if p not in resolved][:30])

    # ------------------------------------------------------------------ interprocedural facts
    def _param_flows(self):
        """For value sites whose callee is a parameter, add the package functions that the
        package's own resolved calls pass for that parameter (one level of argument flow)."""
        incoming: dict[tuple, set] = {}
        for s in self.sites:
            if s.kind != "call" or not s.callbacks:
                continue
            node = self._find_call(s)
            if node is None:
                continue
            for target in s.resolved:
                f = self.funcs.get(target)
                if f is None or f.kind == "module":
                    continue
                params = f.params[1:] if f.cls and f.params and f.params[0] in ("self", "cls") else f.params
                scope = self._scope_for_node(s.caller) or self.module_scopes[s.module]
                for i, a in enumerate(node.args):
                    if i < len(params):
                        for v in self.resolve(a, scope, 3):
                            if v[0] in ("func", "bound", "decorated", "class"):
                                incoming.setdefault((target, params[i]), set()).update(self.targets_of(v) if v[0] == "class" else [v[1]])
                for k in node.keywords:
                    if k.arg:
                        for v in self.resolve(k.value, scope, 3):
                            if v[0] in ("func", "bound", "decorated", "class"):
                                incoming.setdefault((target, k.arg), set()).update(self.targets_of(v) if v[0] == "class" else [v[1]])
        self.param_flows = incoming
        for s in self.sites:
            if s.kind != "call":
                continue
            node = self._find_call(s)
            if node is None or not isinstance(node.func, ast.Name):
                continue
            scope = self._scope_for_node(s.caller) or self.module_scopes[s.module]
            for v in self.resolve(node.func, scope, 2):
                if v[0] == "param":
                    for t in sorted(incoming.get((v[1], v[2]), ())):
                        if t not in s.resolved and t not in s.candidates and t in self.funcs:
                            s.candidates.append(t)

    def _find_call(self, s):
        key = (s.module, s.line, s.col)
        if not hasattr(self, "_call_index"):
            self._call_index = {}
            for mod, m in self.modules.items():
                for n in ast.walk(m["tree"]):
                    if isinstance(n, ast.Call):
                        self._call_index[(mod, n.lineno, n.col_offset + 1)] = n
        return self._call_index.get(key)

    # ------------------------------------------------------------------ outputs
    def nodes(self):
        return sorted(self.funcs)

    def outline(self, max_lines=400):
        """A compact textual symbol table of the package for the prompts."""
        lines = []
        for mod in sorted(self.modules):
            lines.append(f"module {mod}")
            ms = self.module_scopes[mod]
            imports = []
            for name, bs in ms.bindings.items():
                for b in bs:
                    if b[0] == "module" and b[1] != name:
                        imports.append(f"{name}={b[1]}")
                    elif b[0] == "from":
                        imports.append(f"{name}={b[1]}.{b[2]}" if b[2] != name else f"{b[1]}.{b[2]}")
            if imports:
                lines.append("  imports: " + ", ".join(sorted(set(imports)))[:600])
            for q, f in sorted(self.funcs.items(), key=lambda x: x[1].lineno):
                if f.module != mod or f.kind == "module" or f.cls:
                    continue
                if q.count(".") - mod.count(".") > 1 and f.kind == "lambda":
                    continue
                deco = f" @{','.join(f.decorators)}" if f.decorators else ""
                lines.append(f"  def {q}({', '.join(f.params)}){deco}")
            for q, c in sorted(self.classes.items(), key=lambda x: x[1].node.lineno):
                if c.module != mod:
                    continue
                bases = ", ".join(b[1] for b in c.bases)
                mro = " > ".join(b[1] for b in c.mro[1:])
                lines.append(f"  class {q}({bases})" + (f" mro: {mro}" if mro and mro != bases else ""))
                meths = []
                for m, mq in c.methods.items():
                    f = self.funcs[mq]
                    d = f"@{','.join(f.decorators)} " if f.decorators else ""
                    meths.append(f"{d}{m}({', '.join(f.params)})")
                if meths:
                    lines.append("    methods: " + "; ".join(meths))
                if c.properties:
                    lines.append("    properties: " + ", ".join(sorted(c.properties)))
                if c.attrs:
                    lines.append("    class attrs: " + ", ".join(f"{k}={unparse(v[0], 40)}" for k, v in list(c.attrs.items())[:12]))
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more lines omitted)"]
        return "\n".join(lines)

    def attr_fact_text(self, names, limit=30):
        out = []
        for n in names:
            for e, s, recv in self.attr_facts.get(n, [])[:6]:
                out.append(f"  {recv}.{n} = {unparse(e, 70)}   (in {s.qname})")
        return "\n".join(out[:limit])

    def numbered_source(self, mod, start=1, end=None):
        lines = self.modules[mod]["lines"]
        end = end or len(lines)
        width = len(str(end))
        return "\n".join(f"{i:>{width}}| {lines[i - 1]}" for i in range(max(1, start), min(end, len(lines)) + 1))


def _dedup(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def load_micro_case(case_dir, **kw):
    case_dir = Path(case_dir)
    files = []
    for p in sorted(case_dir.rglob("*.py")):
        parts = list(p.relative_to(case_dir).with_suffix("").parts)
        if parts[-1] == "__init__" and len(parts) > 1:
            parts.pop()
        files.append((".".join(parts), p))
    tops = sorted({m.split(".")[0] for m, _ in files})
    return Program(files, tops, **kw)


def load_macro_project(project, **kw):
    """project: a pycg-evaluation projects.Project."""
    files = [(project.module_name(p), p) for p in project.source_files()]
    return Program(files, project.package_names, **kw)
