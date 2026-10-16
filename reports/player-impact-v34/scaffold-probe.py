from pathlib import Path
R=Path('reports/player-impact-v34');O=Path('reports/player-impact-v31')
for name in ['ovr-worker.mjs','ovr-probe.mjs','summarize-probe.py','verify-supplement.py']:
 text=(O/name).read_text(encoding='utf-8').replace('reports/player-impact-v31','reports/player-impact-v34')
 text=text.replace("r['v31']","r['v34']").replace('v31=estimate','v34=estimate').replace('Current v31','Current v34')
 text=text.replace('Source-self restriction vs frozen v30.','Joint source-self floor vs frozen v30.').replace('Source self-role restriction applies to actual cards and synthetic profiles, new v31 source contexts;','Source self-role floor flow applies to actual cards and synthetic profiles, new v34 source contexts;')
 text=text.replace('Self-role restriction and context recentering','Self/receive flow and context recentering')
 f=R/name;assert not f.exists();f.write_text(text,encoding='utf-8')
print('Created matching10-player workload probe against archived v30.')
