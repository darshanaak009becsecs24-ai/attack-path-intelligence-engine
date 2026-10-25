from pathlib import Path
from src.data_loader import load_relationships
from src.graph_builder import build_graph, critical_assets

def test_graph_is_directed_and_contains_asset():
    f=load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")
    g=build_graph(f)
    assert g.is_directed() and g.has_edge("analyst01","Finance-Readers")
    assert "Payroll-Records" in critical_assets(g)

def test_empty_graph_is_supported():
    import pandas as pd
    from src.data_loader import REQUIRED_COLUMNS
    assert build_graph(pd.DataFrame(columns=REQUIRED_COLUMNS)).number_of_nodes()==0
