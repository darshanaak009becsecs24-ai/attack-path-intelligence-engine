"""Reproducible simulated edge-removal remediation."""
import pandas as pd
from .graph_builder import build_graph
from .path_analyzer import discover_paths

def simulate_remediation(frame: pd.DataFrame, weakness: str, max_length: int = 6, max_paths: int = 100) -> dict:
    before_frame = frame.copy(deep=True)
    after_frame = before_frame[before_frame["weakness"].str.casefold() != weakness.casefold()].copy().reset_index(drop=True)
    before = discover_paths(build_graph(before_frame), max_length, max_paths)
    after = discover_paths(build_graph(after_frame), max_length, max_paths)
    before_keys = {tuple(p["nodes"]): p for p in before}
    after_keys = {tuple(p["nodes"]): p for p in after}
    return {"before_frame": before_frame, "after_frame": after_frame, "before_paths": before, "after_paths": after,
            "removed_paths": [before_keys[k] for k in before_keys.keys() - after_keys.keys()],
            "remaining_paths": list(after), "simulated_weakness": weakness}

def recommendation(weakness: str, relationship: str) -> str:
    low = weakness.lower()
    if "admin" in low or "privilege" in low: action = "Remove unnecessary administrative permissions and enforce least privilege."
    elif "credential" in low or "password" in low or "secret" in low: action = "Rotate the affected credential, store it in an approved vault, and review its usage."
    elif "trust" in low: action = "Review and restrict the trust relationship to required principals and scope."
    elif "audit" in low or "logging" in low: action = "Enable appropriate security auditing and alert on sensitive access."
    elif "service" in low: action = "Harden the service account, deny interactive logon, and constrain its permissions."
    else: action = "Review the relationship and remove or constrain access that is not operationally required."
    return f"{action} Related modeled relationship: {relationship}. Simulating removal of '{weakness}' removes matching rows from the analysis copy only."
