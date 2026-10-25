from __future__ import annotations
from pathlib import Path
import logging
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from src.data_loader import load_relationships, DatasetValidationError
from src.graph_builder import build_graph
from src.path_analyzer import discover_paths, explain_path
from src.remediation import simulate_remediation, recommendation
from src.report_generator import make_report, json_bytes, csv_bytes

ROOT = Path(__file__).parent
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Attack Path Intelligence Engine", page_icon="🛡️", layout="wide")
st.markdown("""<style>.stApp{background:#09111d;color:#e7edf5}.block-container{padding-top:1.4rem}.metric-card{background:#121f30;border:1px solid #22364b;border-radius:12px;padding:16px}.muted{color:#9bb0c7}</style>""", unsafe_allow_html=True)
st.title("Attack Path Intelligence Engine")
st.caption("Graph-based risk analysis and simulated remediation · Educational lab only")
st.info("Scores are transparent prioritization estimates, not probabilities of compromise. All remediation is simulated in memory; no infrastructure is changed.")

with st.sidebar:
    st.header("Environment")
    uploaded = st.file_uploader("Upload relationship CSV", type=["csv"], help="Maximum 2 MB and 20,000 rows")
    source_label = "sample_environment.csv"
    try:
        frame = load_relationships(uploaded if uploaded else ROOT / "data" / "sample_environment.csv")
        if uploaded: source_label = uploaded.name
    except DatasetValidationError as exc:
        st.error(str(exc)); st.stop()
    max_length = st.slider("Maximum path length", 1, 10, 6)
    max_paths = st.slider("Maximum paths to inspect", 1, 1000, 100)
    search = st.text_input("Filter identities / assets", placeholder="e.g. analyst01")

graph = build_graph(frame)
paths = discover_paths(graph, max_length, max_paths)
assets = sum(a.get("node_type", "").lower() in {"asset", "critical_asset"} for _, a in graph.nodes(data=True))
identities = sum(a.get("node_type", "").lower() in {"user", "service_account", "identity"} for _, a in graph.nodes(data=True))
high = sum(p["risk"]["category"] in {"High", "Critical"} for p in paths)
c1,c2,c3,c4=st.columns(4)
for col,label,value in [(c1,"Assets",assets),(c2,"Identities",identities),(c3,"Potential paths",len(paths)),(c4,"High / critical paths",high)]: col.metric(label,value)

left,right=st.columns([1.45,1])
with left:
    st.subheader("Environment relationship graph")
    pos=nx.spring_layout(graph,seed=17)
    edge_x=[];edge_y=[]
    for u,v in graph.edges(): edge_x += [pos[u][0],pos[v][0],None];edge_y += [pos[u][1],pos[v][1],None]
    edge_trace=go.Scatter(x=edge_x,y=edge_y,mode="lines",line=dict(width=1.2,color="#40566e"),hoverinfo="none")
    node_x=[];node_y=[];labels=[];colors=[];hover=[]
    for n,attrs in graph.nodes(data=True):
        node_x.append(pos[n][0]);node_y.append(pos[n][1]);labels.append(n)
        t=attrs.get("node_type","").lower();colors.append("#ff6b6b" if t in {"asset","critical_asset"} else "#69d2a2" if t in {"user","service_account","identity"} else "#76a9fa")
        hover.append(f"{n}<br>Type: {attrs.get('node_type')}")
    nodes=go.Scatter(x=node_x,y=node_y,mode="markers+text",text=labels,textposition="top center",hovertext=hover,hoverinfo="text",marker=dict(size=19,color=colors,line=dict(width=1,color="#dce8f4")))
    fig=go.Figure([edge_trace,nodes]);fig.update_layout(height=470,margin=dict(l=0,r=0,t=8,b=0),paper_bgcolor="#09111d",plot_bgcolor="#09111d",font_color="#dce8f4",showlegend=False,xaxis=dict(visible=False),yaxis=dict(visible=False))
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader("Risk distribution")
    counts=pd.Series([p["risk"]["category"] for p in paths],dtype="string").value_counts().reindex(["Critical","High","Medium","Low"],fill_value=0)
    chart=go.Figure(go.Bar(x=counts.index,y=counts.values,marker_color=["#ff5d5d","#ff9f43","#f5ca52","#55c595"]))
    chart.update_layout(height=250,margin=dict(l=0,r=0,t=8,b=0),paper_bgcolor="#09111d",plot_bgcolor="#09111d",font_color="#dce8f4",yaxis_title="Paths")
    st.plotly_chart(chart,use_container_width=True)
    st.caption(f"Analyzed {len(frame)} unique modeled relationships from {source_label}.")

st.subheader("Potential attack paths")
rows=[]
for i,p in enumerate(paths):
    row={"Path":f"P-{i+1:03}","Starting identity":p["start"],"Target asset":p["target"],"Steps":p["length"],"Risk score":p["risk"]["score"],"Risk":p["risk"]["category"],"Weaknesses":", ".join(p["weaknesses"])}
    if not search or search.casefold() in (p["start"]+p["target"]+" ".join(p["nodes"])).casefold(): rows.append(row)
df=pd.DataFrame(rows)
if df.empty: st.caption("No paths match the current filter.")
else:
    st.dataframe(df,use_container_width=True,hide_index=True)
    selected=st.selectbox("Inspect a path",df["Path"].tolist())
    p=paths[int(selected.split("-")[1])-1]
    with st.expander(f"{selected}: {' → '.join(p['nodes'])}",expanded=True):
        st.write(explain_path(p));st.write(f"**Relationships:** {' → '.join(p['relationships'])}")
        st.write(f"**Risk:** {p['risk']['score']}/100 · {p['risk']['category']} · Factors: {p['risk']['factors']}")
        for edge in p["edges"]:
            if edge["weakness"] and edge["weakness"].lower()!="none": st.markdown(f"- **{edge['weakness']}** ({edge['severity']}) — {recommendation(edge['weakness'],edge['relationship'])}")

st.subheader("Simulated remediation comparison")
weaknesses=sorted({w for w in frame.weakness if w and w.lower()!="none"})
if weaknesses:
    selected_weakness=st.selectbox("Mark a modeled weakness as remediated",weaknesses)
    comparison=simulate_remediation(frame,selected_weakness,max_length,max_paths)
    before_avg=round(sum(p["risk"]["score"] for p in comparison["before_paths"])/max(1,len(comparison["before_paths"])),1)
    after_avg=round(sum(p["risk"]["score"] for p in comparison["after_paths"])/max(1,len(comparison["after_paths"])),1)
    a,b,c=st.columns(3);a.metric("Paths before → after",f"{len(comparison['before_paths'])} → {len(comparison['after_paths'])}");b.metric("Removed paths",len(comparison["removed_paths"]));c.metric("Average path score",f"{before_avg} → {after_avg}",delta=round(after_avg-before_avg,1))
    st.caption("Simulated only: the original uploaded or sample dataset remains unchanged.")
    if comparison["removed_paths"]: st.write("**Paths removed:**",[" → ".join(p["nodes"]) for p in comparison["removed_paths"]])
else: comparison=None; st.caption("No modeled weaknesses are available to simulate.")

report=make_report(frame,paths,source_label,comparison if weaknesses else None)
x,y=st.columns(2)
x.download_button("Download JSON report",json_bytes(report),file_name="attack_path_report.json",mime="application/json")
y.download_button("Download CSV paths",csv_bytes(report),file_name="attack_path_paths.csv",mime="text/csv")
with st.expander("Data schema and safety"):
    st.write("Required columns: source, target, relationship, source_type, target_type, source_privilege, weakness, severity, asset_criticality, business_impact. Passwords, tokens, and secrets are not fields in this schema.")
    st.write("The analysis is local and read-only. Uploaded CSVs are bounded, validated, and used only to build an in-memory graph.")
