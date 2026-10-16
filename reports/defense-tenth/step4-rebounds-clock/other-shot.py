import pathlib,json,numpy as np
r=pathlib.Path('reports/defense-tenth/step4-rebounds-clock');load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf-8'));p=load(r/'protocol.json');real=load('reports/defense-tenth/step4-rebounds-after/real.json');out={}
for s in p['seasons']:
 def calc(rows):
  x=[z['seconds'] for z in rows if z['category']=='otherShot' and z.get('seconds') is not None];return {'samples':len(x),'meanSeconds':float(np.mean(x)),'medianSeconds':float(np.median(x))}
 out[s]={'real':calc([z for g in real[s]['games'] for z in g['rows']])};valid={g['id'] for g in real[s]['games']}
 for v,folder,tag in [('allocation','step4-rebounds-after','allocation'),('putback','step4-rebounds-putback-time','putback'),('calibrated','step4-rebounds-clock','calibrated')]:
  vals=[]
  for seed in p['diagnosticSeeds']:
   d=load(f'reports/defense-tenth/{folder}/runs/{s}-{tag}-{seed}.json');vals.append(calc([z for m,g in zip(d['matches'],d['postOreb']['games']) if m['id'] in valid for z in g]))
  out[s][v]={'samplesBySeed':[x['samples'] for x in vals],'meanSeconds':float(np.mean([x['meanSeconds'] for x in vals])),'medianSecondsMean':float(np.mean([x['medianSeconds'] for x in vals]))}
(r/'other-shot-diagnostic.json').write_text(json.dumps({'definition':'same preregistered otherShot category; not latent putback intent, includes delayed same-player shots; descriptive sensitivity only, no adoption claim','seasons':out,'equalSeasonMeanSeconds':{v:float(np.mean([out[s][v]['meanSeconds'] for s in p['seasons']])) for v in ['real','allocation','putback','calibrated']}},indent=2));print(json.dumps(out,indent=2))
