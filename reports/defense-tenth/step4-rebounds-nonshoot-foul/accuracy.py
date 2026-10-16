import pathlib,json,numpy as np
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(R/'protocol.json');t=load(R.parent/'step4-rebounds-turnover-time/seed-arrays.json');rng=np.random.default_rng(p['bootstrapSeed']);B=p['bootstrapDraws'];draw=rng.integers(0,30,(B,30));w=np.stack([(draw==i).sum(1) for i in range(30)],1);sd=rng.integers(0,3,(B,3));bs={};points={};extra={}
for version in ['baseline','candidate']:
 se=[];we=[];nerr=[];werr=[]
 for s in p['seasons']:
  ns=[];ws=[];os=[];ds=[]
  for seed in p['seeds']:
   r=load(R/f'runs/{s}-{version}-{seed}.json');by={x['id']:x for x in r['teams']};ids=t[s]['ids'];ns.append([(by[i]['stats']['pts']-by[i]['opponent']['pts'])/by[i]['games'] for i in ids]);ws.append([by[i]['wins'] for i in ids]);games=sum(x['games'] for x in r['teams']);os.append(sum(x['stats']['oreb'] for x in r['teams'])/games);ds.append(sum(x['stats']['dreb'] for x in r['teams'])/games)
  ns=np.array(ns);ws=np.array(ws);ne=ns[sd].mean(1)-np.array(t[s]['truth']['net']);wv=ws[sd].mean(1)-np.array(t[s]['truth']['wins']);se.append((w*ne**2).sum(1)/30);we.append(((w*abs(wv)).sum(1)/30,(w*wv**2).sum(1)/30));nerr.extend(ns.mean(0)-np.array(t[s]['truth']['net']));werr.extend(ws.mean(0)-np.array(t[s]['truth']['wins']));extra.setdefault(s,{})[version]={'orebPerGame':float(np.mean(os)),'drebPerGame':float(np.mean(ds))}
 bs[version]={'netRMSE':np.sqrt(np.mean(se,0)),'winsMAE':np.mean([v[0] for v in we],0),'winsRMSE':np.sqrt(np.mean([v[1] for v in we],0))};points[version]={'netRMSE':float(np.sqrt(np.mean(np.array(nerr)**2))),'winsMAE':float(np.mean(abs(np.array(werr)))),'winsRMSE':float(np.sqrt(np.mean(np.array(werr)**2)))}
o={'note':'three seeds; paired franchise and seed 20k bootstrap; development in-sample; no adoption or generalization claim','versions':points,'candidateMinusBaseline':{k:{'delta':points['candidate'][k]-points['baseline'][k],'joint95':np.quantile(bs['candidate'][k]-bs['baseline'][k],[.025,.975]).tolist()} for k in points['baseline']},'reboundPerGame':extra};(R/'accuracy-joint.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf8');print(json.dumps(o,indent=2))
