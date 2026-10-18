from pathlib import Path
root=Path('reports/player-impact-v5')
for name in ['input.mjs','worker.mjs','run.mjs','score.py']:
 s=Path('reports/player-impact-v4',name).read_text(encoding='utf-8').replace('player-impact-v4','player-impact-v5').replace('balanced-source-opportunity-4','observed-fresh-zone-foul-5').replace('balanced-flow','profile-flow').replace('balanced-contests','profile-contests')
 (root/name).write_text(s,encoding='utf-8')
s=Path('reports/player-impact-v4/engine.mjs').read_text(encoding='utf-8').replace('player-impact-v4','player-impact-v5').replace('balanced-flow','profile-flow').replace('balanced-contests','profile-contests').replace('{opportunityPlan,contestHelp}','{opportunityPlan,contestHelp,freshZoneProbability,observedFoulInputs}')
anchor=' // Keep the already verified'
block=r''' {
  replace('return fourthProbability(os[i],','const originalProbability=fourthProbability(os[i],');
  replace('},ds,opt);\n    };','},ds,opt); return freshZoneProbability(originalProbability,os[i],putback!==null);\n    };');
  patches.push(`{const start=g.indexOf('    const foulInputs=Object.fromEntries(zones.map(z=>{'),end=g.indexOf('    // p.zone describes recorded FGA.',start);if(start<0||end<0)throw Error('Foul input anchor drift');g=g.slice(0,start)+'    const foulInputs=observedFoulInputs(p,ls[off][hi],opt,attemptMakeProbability);\\n'+g.slice(end);}`);
 }
'''
s=s.replace(anchor,block+anchor)
# Keep memoized and uncached semantics identical after the probability wrapper.
s=s.replace("replace('return fourthProbability(os[i],','const cachedProbability=fourthProbability(os[i],');", "replace('const originalProbability=fourthProbability(os[i],','const originalProbability=fourthProbability(os[i],');")
s=s.replace("replace('},ds,opt);\\n    };','},ds,opt); if(opt.ovrCache)opt.ovrCache.set(cacheKey,cachedProbability); return cachedProbability;\\n    };');", "replace('return freshZoneProbability(originalProbability,os[i],putback!==null);','const cachedProbability=freshZoneProbability(originalProbability,os[i],putback!==null); if(opt.ovrCache)opt.ovrCache.set(cacheKey,cachedProbability); return cachedProbability;');")
(root/'engine.mjs').write_text(s,encoding='utf-8')
