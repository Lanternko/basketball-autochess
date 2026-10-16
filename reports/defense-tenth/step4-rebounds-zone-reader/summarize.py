import pathlib,json,numpy as np
R=pathlib.Path(__file__).parent;load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));real=load(R/'real.json');old=load(R.parent/'step4-rebounds-paths/real.json');audit=load(R/'source-audit.json');out={}
for season,x in real.items():
 rows=[r for g in x['games'] for r in g['rows'] if r['first']];prior=[r for g in old[season]['games'] for r in g['rows'] if r['first']];assert len(rows)==len(prior)
 fg=[r for r in rows if r['firstFgZone'] is not None];pc=audit[season];q={k:sum(r[k] for r in rows)/len(rows) for k in ['oldQuickProxy','quickProxy','quickUnknown']}
 # All first FG events, including the rare FG after FT-first.
 bins={z:{'n':sum(r['firstFgZone']==z for r in fg),'made':sum(r['firstFgZone']==z and r['firstFgMade'] for r in fg)} for z in ['short','mid','long','unknown']}
 out[season]={'firstAnchors':len(rows),'firstFgEvents':len(fg),'oldFirstFgZoneCounts':{z:sum(r['firstFgZone']==z for r in prior) for z in ['short','mid','long']},'newFirstFgZoneCounts':bins,'quickProxy':q,'allFG':{'n':sum(pc['transitions'].values()),'repaired':pc['transitions'].get('mid->short',0),'unknown':len(pc['unknown']),'transitions':pc['transitions']},'unresolvedExamples':pc['unknown'][:12]}
pooled={'quickProxy':{k:float(np.mean([x['quickProxy'][k] for x in out.values()])) for k in ['oldQuickProxy','quickProxy','quickUnknown']},'unknownFirstFgShare':float(np.mean([x['newFirstFgZoneCounts']['unknown']['n']/x['firstFgEvents'] for x in out.values()])),'sourceQualityOnlyNotSimulationPerformance':True}
(R/'summary.json').write_text(json.dumps({'seasons':out,'pooled':pooled},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'pooled':pooled,'counts':{s:x['allFG'] for s,x in out.items()}},indent=2))
