from pathlib import Path
R=Path('reports/player-impact-v39');text=Path('reports/player-impact-v37/run.mjs').read_text(encoding='utf-8').replace('player-impact-v37','player-impact-v39')
a=text.index("const files=");b=text.index('const verify=',a)
text=text[:a]+'''const files=['input.mjs','engine.mjs','worker.mjs','run.mjs','scaffold.py','make-run.py','fit.json','selection.json','solver-repair-protocol.json','fit-verification.json'].map(f=>root+'/'+f).concat(['src/measured_block_events.js','test/measured_block_events.js']);
const hashes={...read('reports/player-impact-v30/validation-protocol.json').hashes,...read(root+'/solver-repair-protocol.json').hashes,...read(root+'/fit.json').hashes,...read(root+'/selection.json').hashes,...Object.fromEntries(files.map(p=>[p,hash(p)]))};
'''+text[b:]
a=text.index("const protocol={");b=text.index("const pf=",a)
text=text[:a]+'''const protocol={version:'competing-block-labels-39',seasons,seeds,variants:['rotation-space'],
 design:read(root+'/protocol-source.json'),hashes};
'''+text[b:];(R/'run.mjs').write_text(text,encoding='utf-8')
