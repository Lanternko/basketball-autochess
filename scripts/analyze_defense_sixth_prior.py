"""No fetching: local coverage evidence and explicit prior-benefit scenarios."""
from defense_sixth_data import *
from scipy.linalg import cho_factor,cho_solve
d=Data(25);model=read('reports/defense-sixth/model-pre25.json');m=model['models']['role'];off=m['priorIntercept']+d.X[:,:d.P]@np.array(m['priorOffense'])+d.X[:,d.P:]@np.array(m['priorDefenseAllowed']);b=np.r_[m['intercept']-m['priorIntercept'],m['offenseResidual'],m['defenseResidual']];mu=d.n[d.train]*np.exp(off[d.train]+d.A[d.train]@b);a=d.A[d.train];information=(a.T@sparse.diags(mu)@a).toarray();H=information+np.diag(np.r_[0,np.full(2*d.P,m['CV']['selected'])]);cf=cho_factor(H)
team_ids=[t['id'] for t in d.league['teams']];V=np.zeros((30,1+2*d.P));minutes={}
for r in d.box:
 if d.order[r['GAME_ID'],r['TEAM_ID']]<=25:minutes[r['TEAM_ID'],r['PLAYER_ID']]=minutes.get((r['TEAM_ID'],r['PLAYER_ID']),0)+r['MIN']
for j,t in enumerate(team_ids):
 total=sum(v for (tid,p),v in minutes.items() if tid==t)
 for (tid,p),v in minutes.items():
  if tid==t:V[j,1+d.pi[p]]=v/total
V-=V.mean(axis=0);s=cho_solve(cf,V.T);var=np.diag(s.T@information@s)*(100*d.leaguePPP)**2;u=float(np.sqrt(var.mean()))
bio={r['PLAYER_ID']:r for r in table('data/benchmark-source/bio.json')};season={}
for r in d.box:
 p=r['PLAYER_ID'];s=season.setdefault(p,dict(minutes=0,GP=0));s['minutes']+=r['MIN'];s['GP']+=1
core=[p for p,s in season.items() if s['GP']>=10 and s['minutes']/s['GP']>=15];rookies=[];eligible=[];unknown=[]
for p in core:
 draft=str(bio.get(p,{}).get('DRAFT_YEAR','unknown'))
 if draft=='2025':rookies.append(p)
 elif draft.isdigit() and int(draft)<2025:eligible.append(p)
 else:unknown.append(p)
baseline=read('reports/defense-fifth/simple-baselines.json')['splits']['25'];basermse=read('reports/defense-fifth/closeout.json')['rolling']['25']['v3']['metrics']['netRMSE'];scenarios=[]
for reduction in [0,.25,.5,.75,1]:
 after=float(np.sqrt(max(0,basermse**2-reduction*u*u)));scenarios.append(dict(residualNoiseVarianceReduction=reduction,netRMSEScenario=after,netRMSEGain=basermse-after))
selected=read('reports/defense-sixth/selection.json');label=selected['cardVersion']+('-neutral' if selected['neutral'] else '')+'-25';runs=[read(f['file']) for f in read('reports/defense-sixth/'+label+'-seeds.json')['files']];pred=[np.mean([(t['stats']['pts']-t['opponent']['pts'])/t['games'] for r in runs for t in r['teams'] if t['id']==tid]) for tid in team_ids];truth=[next(t['trueNet'] for t in baseline['teams'] if t['id']==tid) for tid in team_ids];current_rmse=metrics(truth,pred)['RMSE'];current_scenarios=[]
for reduction in [0,.25,.5,.75,1]:
 after=float(np.sqrt(max(0,current_rmse**2-reduction*u*u)));current_scenarios.append(dict(residualNoiseVarianceReduction=reduction,netRMSEScenario=after,netRMSEGain=current_rmse-after))
save('prior-feasibility.json',dict(majorRotationPlayers=len(core),known2025DrafteesNo2024NBA=rookies,pre2025DraftEligibleNotVerified=eligible,undraftedOrUnknownNotVerified=unknown,verifiedLocal2024_25Players=0,coverageStatement='No cached 2024-25 regular-season dataset; eligibility is not proof of actual prior-season appearances. Draft2025 rookies have no priorNBA data; undrafted and previous draftees need ID/GP joins. No network calls.',pre25ResidualCoefficientSamplingNoiseTeamSD=u,conditionalScenarios=scenarios,currentCardScenarios=current_scenarios,method='Training25 observed-Fisher ridge sampling covariance, box/role prior held fixed, team pre25 minute weights, offensive residual only; joint defense residual is a nuisance control and is not injected into selected cards. Hypothetical older data reduces this one residual-noise component by0..100%; does not estimate old/current ability correlation or prior-box noise, bias, age/injury changes. Not a verified expected gain or total upper bound. No prior-season outcomes exist locally, so total realistic benefit cannot be identified.',requiredData=['2024-25 player IDs/GP/MIN/base box + advanced usage/efficiency + position/age and team stints (minimum3 league endpoints)','60 prior-season defensive tracking endpoints if preserving old contest signals','For lineup prior: approximately1230 PBP +1230 box/starting-lineup files, trading identity joins and strict reconstruction audits'],effortEstimate='Minimal box prior: roughly1-2 engineering days for joins, age/rookie fallback and train-onlyCV; lineup prior adds2-4 days to fetch/reconstruct/audit, network duration uncertain. Estimates based on reuse of present tools, not executed timings.'))
print('PRIOR',len(core),len(rookies),len(eligible),len(unknown),u,scenarios,flush=True)
