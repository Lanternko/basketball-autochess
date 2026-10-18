from defense_sixth_data import *
d=Data(41);m=read('reports/defense-sixth/model-pre41.json');s=m['models']['role'];offset=s['priorIntercept']+d.X[:,:d.P]@np.array(s['priorOffense'])+d.X[:,d.P:]@np.array(s['priorDefenseAllowed']);raw,diag=fit_count(d,d.train,0,offset)
result=read('reports/defense-sixth/diagnosis.json');lg=100*d.leaguePPP
for rows in result['fourTeams'].values():
 for r in rows:
  i=d.pi[r['id']];r['newModelPriorOffense']=lg*s['priorOffense'][i];r['newModelPriorDefenseAllowed']=lg*s['priorDefenseAllowed'][i];r['newModelUnshrunkOffense']=lg*(s['priorOffense'][i]+raw[1+i]);r['newModelUnshrunkDefenseAllowed']=lg*(s['priorDefenseAllowed'][i]+raw[1+d.P+i]);r['newModelShrunkOffense']=lg*(s['priorOffense'][i]+s['offenseResidual'][i]);r['newModelShrunkDefenseAllowed']=lg*(s['priorDefenseAllowed'][i]+s['defenseResidual'][i]);r['newModelShrinkLambda']=s['CV']['selected']
result['unshrunkDiagnostic']={'fit':diag,'definition':'Unpenalized MLE residual on the same pre41 scoring model and box/role prior, fixed centered gauge. Coefficients of unobserved or collinear players are not uniquely identified; an optimizer representative only, never engine inputs. All new-model values are relative log-rate effects times training league100PPP, not OVR or causal player ratings.'}
save('diagnosis.json',result)
print('SHRINK DIAGNOSTIC',diag,flush=True)
