"""Small reusable public recommendation helper."""
from .remediation import recommendation

def recommendations_for_paths(paths):
    return sorted({recommendation(e["weakness"], e["relationship"]) for p in paths for e in p["edges"] if e["weakness"] and e["weakness"].lower() != "none"})
