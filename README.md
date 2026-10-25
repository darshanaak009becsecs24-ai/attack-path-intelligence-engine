# Attack Path Intelligence Engine

A local educational lab that turns modeled identity, permission, system, weakness, and asset relationships into bounded graph searches and transparent remediation priorities. It is defensive analysis software: it does not exploit, authenticate to, or modify infrastructure.

## Features

- Validated CSV input (2 MB / 20,000 row limits; required schema and enumerated values).
- Directed NetworkX graph with identity-to-critical-asset simple-path discovery, configurable bounds, and risk explanations.
- Rule-based 0–100 risk estimate with visible weighted factors; it is not a probability of compromise.
- Streamlit dashboard with graph and risk charts, path filters, detailed inspection, and JSON/CSV exports.
- Reproducible in-memory simulated remediation and before/after comparison.
- Notebook walkthrough, Pytest suite, architecture/methodology/limitations notes, and bootcamp report.

## Architecture

`app.py` is the Streamlit interface. `src/data_loader.py` validates input; `graph_builder.py` models directed relationships; `path_analyzer.py` discovers bounded simple paths; `risk_engine.py` scores them; `remediation.py` filters a separate analysis copy; and `report_generator.py` serializes results. See [docs/architecture.md](docs/architecture.md).

## Prerequisites

Python 3.11 or newer and pip. Windows PowerShell and Linux/macOS shell commands follow.

## Installation

Windows PowerShell:

```powershell
cd attack-path-intelligence-engine
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
cd attack-path-intelligence-engine
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the notebook

From the repository folder after activating the environment:

```bash
jupyter notebook DarshanaAK_Build_attack_path_analysis_engine.ipynb
```

Run all cells from top to bottom. The notebook uses the included sample CSV and runs core analysis, a simulated remediation, visualizations, and the unit test suite. `notebook`, `nbformat`, `nbclient`, and `ipykernel` are listed for notebook execution.

## Launch the dashboard

Windows PowerShell:

```powershell
streamlit run app.py
```

Linux/macOS:

```bash
streamlit run app.py
```

The app uses the included `data/sample_environment.csv` by default. Upload a CSV through the sidebar to analyze another modeled environment.

## Dataset format

The CSV must contain these columns:

`source,target,relationship,source_type,target_type,source_privilege,weakness,severity,asset_criticality,business_impact`

Severity and criticality values: `none`, `low`, `medium`, `high`, `critical`. Business impact allows `low`, `medium`, `high`, `critical`; starting privilege allows `low`, `medium`, `high`, `admin`. Each row describes a directed relationship from source to target. `data/sample_environment.csv` is synthetic. Do not place credentials, tokens, or secret values in these fields.

## Testing

```bash
python -m pytest -q
```

The tests cover valid sample data, missing columns, invalid severity, empty schema, malformed CSV, graph construction, bounded paths, and simulated remediation.

## Report generation

The dashboard provides downloadable JSON and CSV analysis reports. The bootcamp Word report is `DarshanaAK_ProjectReport.docx`. Regenerate it from the repository folder with `python generate_report.py`. The script uses the implementation description and synthetic sample analysis. It explicitly records when a live dashboard screenshot or test execution was unavailable; it does not invent either.

## Example results

The included synthetic sample contains 10 modeled relationships, 3 low/medium-privilege identities, and 2 critical-asset nodes. With default limits, the app finds paths from `analyst01` and `svc_backup` to `Payroll-Records`; selecting the `overbroad_share_permission` weakness simulates removing the analyst path while retaining independent paths where applicable. Results are computed from the sample and can be reproduced in the notebook.

## Limitations

This tool analyzes only relationships present in the CSV. It does not verify real permissions, discover systems, model time or exploitability, or calculate validated compromise likelihood. Graph paths represent possible modeled reachability, not confirmed attacks. See [docs/limitations.md](docs/limitations.md).

## Ethical-use statement

Use only synthetic data or data you are authorized to analyze. This application is read-only and educational. It never executes attacks, changes infrastructure, or requests secrets. Simulated remediation only removes matching weakness rows from a separate analysis copy.
