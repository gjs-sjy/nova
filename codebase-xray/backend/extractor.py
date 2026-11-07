"""
extractor.py — reads Python files with the built-in `ast` module and pulls out:
  - every function / method (name, class, line range, source code, decorators)
  - every function call (who calls what)
  - every import

We only READ the code as text. We never run it.

Run it directly to see what it finds in the sample project:
    python3 extractor.py ../sample_project
"""

import ast
import os
import sys

# Folders we never look inside.
IGNORED_DIRS = {"venv", ".venv", "env", "__pycache__", ".git", "node_modules", "site-packages"}


class CodeVisitor(ast.NodeVisitor):
    """Walks one file's syntax tree and collects functions, calls, and imports."""

    def __init__(self, rel_path, source_lines):
        self.file = rel_path              # e.g. "payment.py"
        self.lines = source_lines         # the file split into lines
        self.stack = []                   # enclosing classes/functions, e.g. [("class", "User"), ("function", "save")]
        self.functions = []
        self.calls = []
        self.imports = []

    # ---------- helpers ----------

    def current_function_id(self):
        """ID of the function we are currently inside, or None if at module level."""
        # Walk the stack from the inside out to find the nearest function.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == "function":
                qualified = ".".join(name for _, name in self.stack[: i + 1])
                return f"{self.file}::{qualified}"
        return None

    def current_class_name(self):
        """Name of the class we are directly inside (for methods), or None."""
        if self.stack and self.stack[-1][0] == "class":
            return self.stack[-1][1]
        return None

    # ---------- classes ----------

    def visit_ClassDef(self, node):
        self.stack.append(("class", node.name))
        self.generic_visit(node)          # visit the methods inside
        self.stack.pop()

    # ---------- functions ----------

    def visit_FunctionDef(self, node):
        class_name = self.current_class_name()
        qualified = ".".join([name for _, name in self.stack] + [node.name])

        # Source code: slice the file's lines (lineno is 1-based, end is inclusive).
        code = "".join(self.lines[node.lineno - 1 : node.end_lineno])

        # Decorators as text, e.g. "app.get" for @app.get("/users").
        decorators = []
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            decorators.append(ast.unparse(target))

        self.functions.append({
            "id": f"{self.file}::{qualified}",
            "name": node.name,
            "file": self.file,
            "class_name": class_name,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "code": code,
            "decorators": decorators,
        })

        # Decorators and default argument values run OUTSIDE the function,
        # so visit them before we step inside.
        for dec in node.decorator_list:
            self.visit(dec)
        for default in node.args.defaults + node.args.kw_defaults:
            if default is not None:
                self.visit(default)

        # Now step inside and visit the body (calls and nested functions).
        self.stack.append(("function", node.name))
        for statement in node.body:
            self.visit(statement)
        self.stack.pop()

    # `async def` works exactly the same way.
    visit_AsyncFunctionDef = visit_FunctionDef

    # ---------- calls ----------

    def visit_Call(self, node):
        callee = None
        if isinstance(node.func, ast.Name):           # foo()
            callee = node.func.id
        elif isinstance(node.func, ast.Attribute):    # obj.foo(), self.foo(), module.foo()
            callee = node.func.attr

        if callee is not None:
            self.calls.append({
                "caller": self.current_function_id(),  # None = module level (entry point!)
                "callee": callee,
                "file": self.file,
                "line": node.lineno,
            })

        self.generic_visit(node)          # calls can be nested: f(g(x))

    # ---------- imports ----------

    def visit_Import(self, node):
        # import os, import a.b as c
        for alias in node.names:
            self.imports.append({"file": self.file, "module": alias.name, "name": None})

    def visit_ImportFrom(self, node):
        # from x import y. node.module is None for "from . import x" — skip those.
        if node.module is None:
            return
        for alias in node.names:
            self.imports.append({"file": self.file, "module": node.module, "name": alias.name})


def extract_file(abs_path, rel_path):
    """Parse one file. Raises SyntaxError / UnicodeDecodeError if the file is bad."""
    with open(abs_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=rel_path)
    visitor = CodeVisitor(rel_path, source.splitlines(keepends=True))
    visitor.visit(tree)
    return {"functions": visitor.functions, "calls": visitor.calls, "imports": visitor.imports}


def extract_project(root):
    """Parse every .py file under `root`. Bad files are skipped, never crash."""
    result = {"files": [], "functions": [], "calls": [], "imports": [], "skipped_files": []}

    for dirpath, dirnames, filenames in os.walk(root):
        # Remove ignored folders so os.walk doesn't go into them.
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)

        for filename in sorted(filenames):
            if not filename.endswith(".py"):
                continue
            abs_path = os.path.join(dirpath, filename)
            # Relative path with forward slashes, e.g. "app/models.py".
            rel_path = os.path.relpath(abs_path, root).replace(os.sep, "/")

            try:
                data = extract_file(abs_path, rel_path)
            except (SyntaxError, UnicodeDecodeError, ValueError):
                result["skipped_files"].append(rel_path)
                continue

            result["files"].append(rel_path)
            result["functions"].extend(data["functions"])
            result["calls"].extend(data["calls"])
            result["imports"].extend(data["imports"])

    return result


if __name__ == "__main__":
    # Milestone 1 checkpoint: print what we found in each file.
    folder = sys.argv[1] if len(sys.argv) > 1 else "../sample_project"
    data = extract_project(folder)

    for file in data["files"]:
        print(f"=== {file}")
        for fn in data["functions"]:
            if fn["file"] == file:
                print(f"  function: {fn['id']}  (lines {fn['start_line']}-{fn['end_line']})")
        for call in data["calls"]:
            if call["file"] == file:
                caller = call["caller"] or "<module level>"
                print(f"  call:     {caller} -> {call['callee']}()")
        for imp in data["imports"]:
            if imp["file"] == file:
                print(f"  import:   {imp['module']}" + (f" . {imp['name']}" if imp["name"] else ""))

    if data["skipped_files"]:
        print("\nSkipped (could not parse):", data["skipped_files"])
