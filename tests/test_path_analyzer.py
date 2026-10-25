from pathlib import Path
import pytest
from src.data_loader import load_relationships
from src.graph_builder import build_graph
from src.path_analyzer import discover_paths
from src.remediation import simulate_remediation

def test_paths_bounded_and_explainable():
    f=load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")
    paths=discover_paths(build_graph(f),max_length=6,max_paths=5)
    assert 0<len(paths)<=5
    assert paths[0]["start"] and paths[0]["target"] and paths[0]["relationships"]

def test_invalid_bounds_rejected():
    with pytest.raises(ValueError): discover_paths(build_graph(load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")),max_length=11)

def test_simulated_fix_removes_matching_exposure_path():
    f=load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")
    out=simulate_remediation(f,"overbroad_share_permission")
    assert out["before_frame"].equals(f) and len(out["after_frame"])<len(f)
    assert len(out["removed_paths"])>=1
