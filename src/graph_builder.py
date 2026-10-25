"""Build directed environment graphs from validated relationship records."""
import networkx as nx
import pandas as pd

def build_graph(frame: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in frame.to_dict("records"):
        for node, kind in ((row["source"], row["source_type"]), (row["target"], row["target_type"])):
            attrs = graph.nodes[node]
            attrs["node_type"] = kind
            attrs["criticality"] = row["asset_criticality"] if kind.lower() in {"asset", "critical_asset"} else attrs.get("criticality", "low")
            attrs["privilege"] = row["source_privilege"] if node == row["source"] else attrs.get("privilege", "low")
        graph.add_edge(row["source"], row["target"], relationship=row["relationship"], weakness=row["weakness"],
                       severity=row["severity"], asset_criticality=row["asset_criticality"], business_impact=row["business_impact"])
    return graph

def critical_assets(graph: nx.DiGraph) -> list[str]:
    return sorted(n for n, a in graph.nodes(data=True) if a.get("node_type", "").lower() in {"asset", "critical_asset"})

def low_privilege_starts(graph: nx.DiGraph) -> list[str]:
    return sorted(n for n, a in graph.nodes(data=True) if a.get("node_type", "").lower() in {"user", "service_account", "identity"}
                  and a.get("privilege", "low") in {"low", "medium"})
