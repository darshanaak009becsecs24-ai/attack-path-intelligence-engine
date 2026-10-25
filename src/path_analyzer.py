"""Bounded simple-path discovery with explicit source and target constraints."""
from __future__ import annotations
import networkx as nx
from .graph_builder import critical_assets, low_privilege_starts
from .risk_engine import score_path

def discover_paths(graph: nx.DiGraph, max_length: int = 6, max_paths: int = 100,
                   starts: list[str] | None = None, targets: list[str] | None = None) -> list[dict]:
    if not 1 <= int(max_length) <= 10: raise ValueError("max_length must be between 1 and 10")
    if not 1 <= int(max_paths) <= 1000: raise ValueError("max_paths must be between 1 and 1000")
    sources = sorted(set(starts if starts is not None else low_privilege_starts(graph)))
    sinks = sorted(set(targets if targets is not None else critical_assets(graph)))
    result = []
    for source in sources:
        for target in sinks:
            if source == target or source not in graph or target not in graph: continue
            try:
                paths = nx.all_simple_paths(graph, source, target, cutoff=max_length)
                for nodes in paths:
                    edges = [dict(graph.edges[u, v]) for u, v in zip(nodes, nodes[1:])]
                    item = {"start": source, "intermediates": nodes[1:-1], "target": target, "nodes": nodes,
                            "edges": edges, "start_privilege": graph.nodes[source].get("privilege", "low"),
                            "length": len(edges), "weaknesses": sorted({e["weakness"] for e in edges if e["weakness"] and e["weakness"].lower() != "none"}),
                            "relationships": [e["relationship"] for e in edges]}
                    item["risk"] = score_path(item)
                    result.append(item)
                    if len(result) >= max_paths: return result
            except (nx.NetworkXError, nx.NodeNotFound):
                continue
    return result

def explain_path(path: dict) -> str:
    weaknesses = ", ".join(path["weaknesses"]) if path["weaknesses"] else "no named weakness"
    return f"{path['start']} can reach critical asset {path['target']} across {path['length']} modeled relationship(s); observed weakness: {weaknesses}. This is a modeled exposure path, not evidence of compromise."
