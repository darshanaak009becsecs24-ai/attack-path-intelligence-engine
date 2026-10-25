"""Safe, bounded CSV loading and validation for modeled security relationships."""
from __future__ import annotations
import io
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)
REQUIRED_COLUMNS = ["source", "target", "relationship", "source_type", "target_type",
                    "source_privilege", "weakness", "severity", "asset_criticality", "business_impact"]
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical", "none"}
ALLOWED_IMPACTS = {"low", "medium", "high", "critical"}
MAX_FILE_BYTES = 2_000_000
MAX_ROWS = 20_000

class DatasetValidationError(ValueError):
    """Raised when an uploaded relationship dataset violates the supported schema."""

def load_relationships(source, max_bytes: int = MAX_FILE_BYTES, max_rows: int = MAX_ROWS) -> pd.DataFrame:
    """Load CSV path, bytes, file-like object, or DataFrame and validate it."""
    try:
        if isinstance(source, pd.DataFrame):
            frame = source.copy()
        else:
            if isinstance(source, (str, Path)):
                path = Path(source)
                if path.stat().st_size > max_bytes:
                    raise DatasetValidationError(f"CSV exceeds the {max_bytes:,}-byte limit.")
                frame = pd.read_csv(path, dtype=str, keep_default_na=False, on_bad_lines="error")
            else:
                raw = source.getvalue() if hasattr(source, "getvalue") else source.read() if hasattr(source, "read") else source
                if isinstance(raw, str): raw = raw.encode("utf-8")
                if not isinstance(raw, (bytes, bytearray)):
                    raise DatasetValidationError("Input must be a CSV path, bytes, file-like object, or DataFrame.")
                if len(raw) > max_bytes:
                    raise DatasetValidationError(f"CSV exceeds the {max_bytes:,}-byte limit.")
                frame = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, on_bad_lines="error")
    except DatasetValidationError:
        raise
    except Exception as exc:
        logger.warning("Could not parse relationship dataset: %s", exc)
        raise DatasetValidationError(f"Could not parse CSV: {exc}") from exc
    frame.columns = [str(c).strip().lower() for c in frame.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise DatasetValidationError("Missing required columns: " + ", ".join(missing))
    if len(frame) > max_rows:
        raise DatasetValidationError(f"CSV has {len(frame):,} rows; limit is {max_rows:,}.")
    frame = frame[REQUIRED_COLUMNS].copy()
    for col in REQUIRED_COLUMNS:
        frame[col] = frame[col].astype(str).str.strip()
    if frame.empty:
        return frame
    for col in ("source", "target", "relationship", "source_type", "target_type"):
        bad = frame[col].eq("")
        if bad.any():
            raise DatasetValidationError(f"Column '{col}' contains blank values at rows {list(frame.index[bad] + 2)[:8]}.")
    if (frame["source"] == frame["target"]).any():
        raise DatasetValidationError("Self-loop relationships are not supported.")
    for col, allowed in (("severity", ALLOWED_SEVERITIES), ("asset_criticality", ALLOWED_SEVERITIES), ("business_impact", ALLOWED_IMPACTS)):
        frame[col] = frame[col].str.lower()
        invalid = sorted(set(frame[col]) - allowed)
        if invalid:
            raise DatasetValidationError(f"Invalid {col} values: {', '.join(invalid)}. Allowed: {', '.join(sorted(allowed))}.")
    frame["source_privilege"] = frame["source_privilege"].str.lower()
    invalid_priv = sorted(set(frame["source_privilege"]) - {"low", "medium", "high", "admin"})
    if invalid_priv:
        raise DatasetValidationError(f"Invalid source_privilege values: {', '.join(invalid_priv)}.")
    # Duplicate edges are collapsed deterministically; the first record is retained.
    frame = frame.drop_duplicates(subset=["source", "target", "relationship"], keep="first").reset_index(drop=True)
    return frame
