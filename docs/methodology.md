# Analysis methodology

## Relationship model

Each CSV row becomes a directed edge `source -> target`. The edge retains relationship type, weakness label and severity, asset criticality, and business impact. Source and target types annotate graph nodes. The default starting set consists of `user`, `service_account`, or `identity` nodes with `low` or `medium` modeled privilege. Targets are nodes typed `asset` or `critical_asset`.

## Path discovery

The engine enumerates NetworkX simple paths, which do not repeat nodes, for each eligible source/target pair. The user can set maximum edge length from 1 to 10 and result count from 1 to 1,000. Results stop at the configured count. The user-provided limits prevent unbounded search, though dense graphs can still consume resources up to those limits.

## Risk estimate

For each path the engine takes the maximum edge weakness severity, asset criticality, and business impact; it also uses the starting node's privilege and edge count. Values are normalized to 0–100 and weighted as follows:

| Factor | Weight / maximum contribution |
|---|---:|
| Asset criticality | 25 |
| Starting privilege | 15 |
| Maximum weakness severity | 30 |
| Business impact | 20 |
| Path proximity | 10 (10 for one edge, reduced 2 per additional edge) |

The sum is rounded and classified as Low (0–34), Medium (35–59), High (60–79), or Critical (80–100). This transparent rule is a prioritization estimate, not validated against incident data and not a probability of compromise.

## Simulated remediation

The user chooses a weakness label. The engine copies the original DataFrame, removes matching weakness rows from the copy, rebuilds the graph, and recomputes paths. The comparison is reproducible for the original input and selection. No external controls are changed or verified.
