import pandas as pd
import pytest
from src.data_loader import load_relationships, DatasetValidationError

def test_sample_loads_and_deduplicates():
    from pathlib import Path
    frame=load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")
    assert len(frame)==10

def test_missing_columns_rejected():
    with pytest.raises(DatasetValidationError,match="Missing required"):
        load_relationships(pd.DataFrame({"source":["a"]}))

def test_invalid_severity_rejected():
    from pathlib import Path
    frame=load_relationships(Path(__file__).parents[1]/"data"/"sample_environment.csv")
    frame.loc[0,"severity"]="extreme"
    with pytest.raises(DatasetValidationError,match="Invalid severity"):
        load_relationships(frame)

def test_empty_valid_schema_is_allowed():
    from src.data_loader import REQUIRED_COLUMNS
    frame=load_relationships(pd.DataFrame(columns=REQUIRED_COLUMNS))
    assert frame.empty

def test_malformed_csv_rejected():
    with pytest.raises(DatasetValidationError,match="Could not parse"):
        load_relationships(b'"unterminated')
