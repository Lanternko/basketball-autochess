from pathlib import Path
R=Path('reports/player-impact-v41')
text=Path('reports/player-impact-v39/run.mjs').read_text(encoding='utf-8').replace('player-impact-v39','player-impact-v41')
a=text.index('const files=');b=text.index('const verify=',a)
text=text[:a]+'''const files=['input.mjs','model.mjs','engine.mjs','worker.mjs','run.mjs','make-run.py','fit.json','selection.json','fit-verification.json','model-verification.json','context-structure-verification.json','verify-contexts.mjs',...seasons.map(s=>s+'-contexts.json')].map(f=>root+'/'+f);
const hashes={...read(root+'/context-protocol.json').hashes,...Object.fromEntries(files.map(p=>[p,hash(p)]))};
'''+text[b:]
a=text.index('const protocol={');b=text.index('const pf=',a)
text=text[:a]+'''const protocol={version:'zone-prior-fresh-fg-defense-41',seasons,seeds,variants:['rotation-space'],
 design:read(root+'/protocol-source.json'),hashes};
'''+text[b:]
assert not (R/'run.mjs').exists()
(R/'run.mjs').write_text(text,encoding='utf-8')
