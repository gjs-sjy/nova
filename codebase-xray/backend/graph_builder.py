"""
graph_builder.py — turns what extractor.py found into a NetworkX graph.

An edge A -> B means "function A calls function B".
From the graph we work out:
  - entry points (where the program starts)
  - unused functions (nobody calls them and they aren't entry points)
  - impact: "if I delete this function, what could break?"

Run it directly to see the contract JSON for the sample project:
    python3 graph_builder.py ../sample_project
"""

import json
import sys

import networkx as nx

from extractor import extract_project

# Decorator endings that mean "this is a web route handler", e.g. @app.get, @router.post.
ROUTE_DECORATORS = {"get", "post", "put", "patch", "delete", "route", "websocket"}


def resolve_callee(callee_name, call_file, functions_by_name):
    """Find which project function a call refers to. Returns its ID, or None to skip."""
    candidates = functions_by_name.get(callee_name, [])

    # 1. Prefer a function with that name in the same file.
    same_file = [fn for fn in candidates if fn["file"] == call_file]
    if len(same_file) == 1:
        return same_file[0]["id"]

    # 2. Else, if exactly one function in the whole project has that name, use it.
    if len(same_file) == 0 and len(candidates) == 1:
        return candidates[0]["id"]

    # 3. Zero matches (builtin/library like print) or ambiguous -> don't guess.
    return None


def is_route_handler(fn):
    """True if the function has a decorator like @app.get or @router.post."""
    for dec in fn["decorators"]:
        last_part = dec.split(".")[-1]        # "app.get" -> "get"
        if "." in dec and last_part in ROUTE_DECORATORS:
            return True
    return False


def build_graph(extracted):
    """Build the call graph from extract_project()'s output."""
    graph = nx.DiGraph()

    # Group functions by name so we can resolve calls quickly.
    functions_by_name = {}
    for fn in extracted["functions"]:
        functions_by_name.setdefault(fn["name"], []).append(fn)

    # Step 1: add every function as a node first.
    for fn in extracted["functions"]:
        graph.add_node(
            fn["id"],
            id=fn["id"],
            name=fn["name"],
            file=fn["file"],
            class_name=fn["class_name"],
            start_line=fn["start_line"],
            end_line=fn["end_line"],
            code=fn["code"],
            is_entry_point=False,
            is_unused=False,
        )

    # Step 2: add an edge for every call we can resolve.
    called_at_module_level = set()
    for call in extracted["calls"]:
        target = resolve_callee(call["callee"], call["file"], functions_by_name)
        if target is None:
            continue
        if call["caller"] is None:
            # Called from outside any function (e.g. if __name__ == "__main__":)
            called_at_module_level.add(target)
        elif call["caller"] in graph and call["caller"] != target:
            # (We skip a function calling itself — recursion isn't a dependency.)
            graph.add_edge(call["caller"], target, type="calls")

    # Step 3: mark entry points and unused functions.
    for fn in extracted["functions"]:
        node = graph.nodes[fn["id"]]
        node["is_entry_point"] = (
            fn["id"] in called_at_module_level
            or fn["name"] == "main"
            or fn["name"].startswith("test_")
            or is_route_handler(fn)
        )
        node["is_unused"] = graph.in_degree(fn["id"]) == 0 and not node["is_entry_point"]

    return graph


def get_impact(graph, node_id):
    """What calls this function, what it calls, and everything that could break without it."""
    # Sort affected functions by how far away they are (closest callers first).
    distances = nx.shortest_path_length(graph, target=node_id)
    all_affected = sorted(nx.ancestors(graph, node_id), key=lambda n: (distances[n], n))

    affected_files = []
    for n in all_affected:
        file = graph.nodes[n]["file"]
        if file not in affected_files:
            affected_files.append(file)

    return {
        "node_id": node_id,
        "direct_callers": sorted(graph.predecessors(node_id)),
        "all_affected": all_affected,
        "calls": sorted(graph.successors(node_id)),
        "affected_files": affected_files,
    }


def graph_to_json(graph, extracted, project_id):
    """Convert the graph into the /upload response shape from the data contract."""
    nodes = [dict(attrs) for _, attrs in graph.nodes(data=True)]
    edges = [
        {"source": source, "target": target, "type": "calls"}
        for source, target in graph.edges()
    ]
    return {
        "project_id": project_id,
        "stats": {
            "files": len(extracted["files"]),
            "functions": len(nodes),
            "calls": len(edges),
            "unused": sum(1 for n in nodes if n["is_unused"]),
            "skipped_files": extracted["skipped_files"],
        },
        "nodes": nodes,
        "edges": edges,
    }


if __name__ == "__main__":
    # Milestone 2 checkpoint: print the contract JSON and a quick summary.
    folder = sys.argv[1] if len(sys.argv) > 1 else "../sample_project"
    extracted = extract_project(folder)
    graph = build_graph(extracted)

    print(json.dumps(graph_to_json(graph, extracted, "sample"), indent=2))

    print("\n--- Summary ---")
    for source, target in graph.edges():
        print(f"edge:        {source} -> {target}")
    for node_id, attrs in graph.nodes(data=True):
        if attrs["is_entry_point"]:
            print(f"entry point: {node_id}")
        if attrs["is_unused"]:
            print(f"unused:      {node_id}")
    if "utils.py::calculate_total" in graph:
        print("impact of calculate_total:", get_impact(graph, "utils.py::calculate_total"))
