from pathlib import Path
R=Path('reports/player-impact-v31');O=Path('reports/player-impact-v30')
def put(name,text):
 p=R/name;assert not p.exists(),p;p.write_text(text,encoding='utf-8')
put('ovr-worker.mjs',(O/'ovr-worker.mjs').read_text(encoding='utf-8'))
p=(O/'ovr-probe.mjs').read_text(encoding='utf-8').replace("root='reports/player-impact-v30'","root='reports/player-impact-v31'")
p=p.replace('Same 10 diagnostic players,','Source-self restriction vs frozen v30. Same 10 diagnostic players,').replace('New source-role creation dependence in actual cards and synthetic profiles, new v30 source contexts; no passing pair quality bonus. Compare to exactly matching archived v29 cap/healthy arms, not raw rankings.','Source self-role restriction applies to actual cards and synthetic profiles, new v31 source contexts; source roles/attributes and workload unchanged. No passing pair quality bonus. Compare to exactly matching archived v30 cap/healthy arms, not raw rankings.')
p=p.replace("...read('reports/player-impact-v29/protocol.json').hashes","...read('reports/player-impact-v30/ovr-probe-protocol.json').hashes")
put('ovr-probe.mjs',p)
s=(O/'summarize-probe.py').read_text(encoding='utf-8').replace("ROOT=Path('reports/player-impact-v30')","ROOT=Path('reports/player-impact-v31')").replace("read('reports/player-impact-v29/checkpoint.json')","read('reports/player-impact-v30/ovr-probe-checkpoint.json')")
s=s.replace('v28','previousVersion').replace('v30','v31').replace('previousVersion','v30')
# The substitutions above must not accidentally redirect the previous checkpoint.
s=s.replace("read('reports/player-impact-v31/ovr-probe-checkpoint.json')","read('reports/player-impact-v30/ovr-probe-checkpoint.json')")
s=s.replace('Current v31 vs archived v29/v30-engine','Current v31 vs archived v30').replace('Context and creation-dependence change also affect synthetic teammates.','Self-role restriction and context recentering also affect synthetic teammates; source roles and attributes unchanged.')
put('summarize-probe.py',s)
print('Created frozen v31 probe runners.')
