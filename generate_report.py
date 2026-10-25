"""Generate the DOCX report using only the Python standard library."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from datetime import datetime

ROOT=Path(__file__).parent
OUT=ROOT/'YourName_Project_Report.docx'

SECTIONS=[
('Abstract',"This project implements a local defensive analysis tool that models security relationships as a directed graph and identifies bounded paths from lower-privilege identities to critical assets. The Streamlit interface presents a graph, path details, a transparent 0–100 prioritization estimate, recommendations, and simulated remediation comparisons. The bundled synthetic sample illustrates the method. Scores are not compromise probabilities and sample findings are not measured enterprise risk."),
('1 Introduction',"Security exposure can arise when permissions, trust relationships, system access, and asset importance combine across multiple steps. A graph view helps analysts inspect modeled reachability and prioritize review."),
('2 Problem Statement',"Analysts need a repeatable way to examine how supplied identity and system relationships connect to critical assets. A useful lab tool must bound graph searches, explain scoring, accept untrusted CSV safely, and compare a simulated fix without claiming to alter or verify real controls."),
('3 Objectives',"Validate a supported CSV schema; model relationships as a directed graph; identify bounded simple paths; provide factor-level triage scores; recommend defensive actions; simulate remediation using a separate copy; and export reproducible results."),
('4 Existing Approach and Limitations',"Manual access reviews and spreadsheet filtering can show direct permissions but make multi-step relationships harder to trace consistently. Enterprise products may depend on connectors, licensed data sources, or environment-specific configuration. This project demonstrates the local graph method but cannot replace a validated governance or exposure-management platform."),
('5 Proposed System',"The application loads the bundled synthetic sample or a CSV upload, validates rows, builds a NetworkX DiGraph, searches simple paths from low/medium-privilege identities to assets, scores each path, and presents explanations. A selected weakness can be removed from a copied frame to recompute paths; the original data remains separate."),
('6 System Architecture',"CSV input -> validation -> directed NetworkX graph -> bounded simple path discovery -> weighted prioritization estimate -> dashboard and exports. A separate remediation branch copies the validated data, removes matching weakness rows, rebuilds the graph, and compares paths. The application has no connection to an enterprise environment."),
('7 Technology Stack',"Python 3.11 or newer; Streamlit for the web interface; NetworkX for graph algorithms; Plotly for interactive visuals; Pandas for tabular data; Pytest for unit tests; Jupyter for the notebook; python-docx is not required by the report generator, which uses the Python standard library."),
('8 Dataset Schema and Sample Data',"Each CSV row describes a directed relationship and carries relationship type, node types, modeled privilege, a weakness label, severity, asset criticality, and business impact. Required columns: source, target, relationship, source_type, target_type, source_privilege, weakness, severity, asset_criticality, business_impact. All included records are synthetic."),
('9 Graph Modeling Methodology',"Each source-target pair becomes a directed edge. Edge attributes retain relationship, weakness, severity, criticality, and business impact. User, service_account, and identity nodes with low or medium privilege are candidate starts. Nodes typed asset or critical_asset are targets. Simple paths do not repeat nodes."),
('10 Attack Path Discovery Algorithm',"For each eligible start and target, the analyzer calls NetworkX all_simple_paths with a configurable edge cutoff. Defaults are six edges and at most 100 returned paths; hard bounds are 10 edges and 1,000 results. The search stops at the configured count. Each path records nodes, intermediate nodes, relationship types, weaknesses, length, and an explanation."),
('11 Risk Scoring Methodology and Example',"The rule-based score combines asset criticality (25 points), starting privilege (15), maximum weakness severity (30), business impact (20), and path proximity (up to 10). Inputs are normalized from ordinal 0–4 levels. Proximity is 10 for one edge and falls by two for each additional edge. Scores are capped at 100: Low 0–34, Medium 35–59, High 60–79, Critical 80–100. Example: critical asset 25 + admin privilege 15 + critical weakness 30 + critical impact 20 + one-edge proximity 10 = 100. This is a triage estimate, not a calibrated likelihood."),
('12 Implementation Details',"Input validation enforces a 2 MB and 20,000-row limit, required columns, nonblank endpoints, allowed categories, and self-loop rejection. Duplicate source/target/relationship rows are collapsed. The UI includes CSV upload, path controls, identity/asset text filtering, graph view, charts, path inspection, recommendations, and JSON/CSV downloads."),
('13 Screenshots of the Running Application',"No screenshot of the actual running Streamlit application was captured in this environment because the project dependencies could not be installed into a usable runtime. No illustrative mockup is presented as a real application screenshot. After installing requirements, run the dashboard and capture it for this section."),
('14 Testing Methodology and Results',"The repository includes tests for sample loading, missing columns, invalid severity, empty valid schema, malformed CSV, graph construction, empty graph, path bounds, risk scoring, and simulated remediation. The suite was not executed in this environment because the dependency installation did not complete. No test pass count is claimed."),
('15 Before and After Remediation Analysis',"The sample includes a path analyst01 -> Finance-Readers -> Finance-Share -> Payroll-DB -> Payroll-Records. Simulating removal of overbroad_share_permission removes the Finance-Share edge from an analysis copy and breaks that route. The svc_backup route remains through Backup-Admins. This is a traced synthetic example; no infrastructure change was made or verified."),
('16 Results and Discussion',"The sample has 10 modeled relationship rows and includes three low/medium-privilege identities and two asset-typed nodes. It is constructed to demonstrate multi-step reachability to Payroll-Records plus an independent short route to Public-Docs. These synthetic outcomes demonstrate the intended model, not operational efficacy."),
('17 Limitations and Ethical Considerations',"The engine analyzes only supplied static relationships. Missing or inaccurate records affect reachability. Ordinal weights are heuristic and unvalidated against incidents, exploitability, or business loss. Weakness removal is coarse. The application does not discover systems, authenticate, exploit, collect secrets, or modify infrastructure. Use synthetic data or data whose analysis is authorized."),
('18 Future Enhancements',"Potential extensions include schema adapters for authorized exports, confidence/provenance metadata, conditional policy modeling, reviewed severity calibration, richer control-specific remediation, accessibility refinements, and larger-graph performance evaluation."),
('19 Conclusion',"The project provides a modular local lab for visualizing modeled attack paths and comparing a simulated remediation. Its bounded search, explicit scoring factors, input validation, and synthetic sample make the analysis understandable for education, provided findings are treated as hypotheses for review."),
('20 References',"NetworkX simple paths documentation: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html\nStreamlit documentation: https://docs.streamlit.io/\nPlotly Python documentation: https://plotly.com/python/\nPandas documentation: https://pandas.pydata.org/docs/\nPython documentation: https://docs.python.org/3/")]

def run(text, bold=False, size=None, color=None):
    props=[]
    if bold: props.append('<w:b/>')
    if size: props.append(f'<w:sz w:val="{size}"/>')
    if color: props.append(f'<w:color w:val="{color}"/>')
    return ('<w:r><w:rPr>'+''.join(props)+'</w:rPr>' if props else '<w:r>')+'<w:t xml:space="preserve">'+escape(text)+'</w:t></w:r>'

def para(text='', style=None, align=None, bold=False, size=None, color=None, pagebreak=False):
    ppr=[]
    if style: ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align: ppr.append(f'<w:jc w:val="{align}"/>')
    if pagebreak: return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    return '<w:p>'+('<w:pPr>'+''.join(ppr)+'</w:pPr>' if ppr else '')+run(text,bold,size,color)+'</w:p>'

body=[para('Attack Path Intelligence Engine','Title',align='center'),para('Graph Based Risk Analysis and Remediation','Subtitle',align='center'),para('Bootcamp Project Report',align='center',bold=True,size=28,color='24618A'),para('Prepared by YourName',align='center'),para('25 October 2026',align='center'),para(pagebreak=True)]
for heading,text in SECTIONS:
    body.append(para(heading,'Heading1'))
    for line in text.split('\n'):
        body.append(para(line))
    if heading.startswith('6 System'):
        body.append(para('Architecture flow: CSV -> Validator -> Directed graph -> Bounded path analysis -> Risk engine -> Dashboard / JSON and CSV reports. Simulated remediation runs as a separate copied-data branch.','Quote',bold=True))
    if heading.startswith('8 Dataset'):
        body.append(para('Sample rows: analyst01 -> Finance-Readers (member_of); Finance-Readers -> Finance-Share (read_access); Finance-Share -> Payroll-DB (network_trust); Payroll-DB -> Payroll-Records (hosts).','Quote'))
body.append(para('Appendix A Risk Factor Weights','Heading1'))
for line in ['Asset criticality: maximum 25 points','Starting privilege: maximum 15 points','Weakness severity: maximum 30 points','Business impact: maximum 20 points','Path proximity: maximum 10 points']:
    body.append(para(line,'ListBullet'))

document_xml='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(body)+'<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="1000" w:bottom="900" w:left="1000"/></w:sectPr></w:body></w:document>'
styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="20"/><w:color w:val="263343"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="40"/><w:color w:val="000000"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:sz w:val="24"/><w:color w:val="24618A"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="300" w:after="120"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="12395B"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:rPr><w:i/><w:color w:val="42617D"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:pPr><w:ind w:left="360"/></w:pPr></w:style></w:styles>'''
rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
docrels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
content='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content);z.writestr('_rels/.rels',rels);z.writestr('word/document.xml',document_xml);z.writestr('word/styles.xml',styles);z.writestr('word/_rels/document.xml.rels',docrels)
print(f'Created {OUT}')
