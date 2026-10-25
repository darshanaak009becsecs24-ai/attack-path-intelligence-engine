"""JSON and CSV report serialization."""
from __future__ import annotations
from datetime import datetime, timezone
import json
import pandas as pd
from .path_analyzer import explain_path
from .remediation import recommendation

def make_report(frame: pd.DataFrame, paths: list[dict], dataset_name: str, comparison: dict | None = None) -> dict:
    paths_out = []
    for p in paths:
        paths_out.append({"start": p["start"], "intermediates": p["intermediates"], "target": p["target"], "nodes": p["nodes"],
                          "relationships": p["relationships"], "weaknesses": p["weaknesses"], "length": p["length"],
                          "score": p["risk"]["score"], "risk_category": p["risk"]["category"], "risk_factors": p["risk"]["factors"],
                          "explanation": explain_path(p), "recommendations": [recommendation(e["weakness"], e["relationship"]) for e in p["edges"]]})
    return {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "dataset": dataset_name,
            "scoring_methodology": "Weighted transparent prioritization estimate: asset criticality 25%, starting privilege 15%, maximum edge weakness severity 30%, business impact 20%, path proximity 10%; capped at 100. Not a probability of compromise.",
            "environment_summary": {"relationships": int(len(frame)), "identities": int(frame.loc[frame.source_type.isin(["user", "service_account", "identity"]), "source"].nunique()),
                                    "assets": int(frame.loc[frame.target_type.isin(["asset", "critical_asset"]), "target"].nunique()), "paths": len(paths)},
            "paths": paths_out, "comparison": ({"simulated_weakness": comparison["simulated_weakness"], "paths_before": len(comparison["before_paths"]),
            "paths_after": len(comparison["after_paths"]), "removed_paths": len(comparison["removed_paths"]),
            "remaining_high_or_critical": sum(p["risk"]["category"] in {"High", "Critical"} for p in comparison["after_paths"])} if comparison else None)}

def json_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")

def csv_bytes(report: dict) -> bytes:
    return pd.DataFrame(report["paths"]).to_csv(index=False).encode("utf-8")
