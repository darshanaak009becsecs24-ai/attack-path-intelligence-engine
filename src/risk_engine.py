"""Transparent prioritization estimate; not a probability of compromise."""
SEV = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
PRIV = {"low": 1, "medium": 2, "high": 3, "admin": 4}

def score_path(path: dict) -> dict:
    edges = path["edges"]
    weakness = max((SEV.get(e["severity"], 0) for e in edges), default=0)
    asset = max((SEV.get(e["asset_criticality"], 0) for e in edges), default=1)
    impact = max((SEV.get(e["business_impact"], 0) for e in edges), default=1)
    privilege = PRIV.get(path.get("start_privilege", "low"), 1)
    steps = len(edges)
    # Weighted 0-100 prioritization estimate. Short paths receive a modest bonus.
    factors = {"asset_criticality": round(asset / 4 * 25, 1), "starting_privilege": round(privilege / 4 * 15, 1),
               "weakness_severity": round(weakness / 4 * 30, 1), "business_impact": round(impact / 4 * 20, 1),
               "path_proximity": round(max(0, 10 - max(0, steps - 1) * 2), 1)}
    score = min(100, round(sum(factors.values())))
    category = "Critical" if score >= 80 else "High" if score >= 60 else "Medium" if score >= 35 else "Low"
    return {"score": score, "category": category, "factors": factors}
