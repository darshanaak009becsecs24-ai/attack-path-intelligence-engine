from src.risk_engine import score_path

def test_score_is_bounded_and_transparent():
    p={"edges":[{"severity":"critical","asset_criticality":"critical","business_impact":"critical"}],"start_privilege":"admin","length":1}
    r=score_path(p)
    assert r["score"]==100 and r["category"]=="Critical"
    assert set(r["factors"])=={"asset_criticality","starting_privilege","weakness_severity","business_impact","path_proximity"}
