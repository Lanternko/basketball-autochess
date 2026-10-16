from register import HERE, ROOT, sha, dump
from datetime import datetime, timezone
import json
import math

def read(f):
    return json.loads(f.read_text(encoding='utf-8'))

def main():
    p=read(HERE/'protocol.json'); before=read(HERE/'protected-before.json')
    lock=read(HERE/'analysis-code-registration.json'); repair=read(HERE/'analysis-code-repair-1.json')
    k=read(HERE/'kernel-results.json'); g=read(HERE/'game-audit.json')
    changed=[f for f,h in before.items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
    new=[f.relative_to(ROOT).as_posix() for s in ['src','scripts','reports/defense-tenth'] for f in (ROOT/s).rglob('*')
         if f.is_file() and HERE not in f.parents and f.relative_to(ROOT).as_posix() not in before]
    checks={
      'protocol':sha(HERE/'protocol.json')==(HERE/'protocol.sha256').read_text(encoding='utf-8').split()[0],
      'registerCode':sha(HERE/'register.py')==p['registrationCodeSHA256'],
      'protectedManifest':sha(HERE/'protected-before.json')==p['protectedManifestSHA256'],
      'protectedFilesUnchanged':not changed,'noNewProtectedFiles':not new,
      'inputsUnchanged':all(sha(ROOT/f)==h for f,h in p['inputHashes'].items()),
      'codeRepairChain':sha(HERE/'analyze-initial.mjs')==lock['sha256']==repair['beforeSHA256'] and sha(HERE/'analyze.mjs')==repair['afterSHA256'],
      'kernelOriginalFilePreserved':sha(HERE/'kernel-results.json')==repair['kernelSHA256Preserved'],
      'repairBeforeAnyGameOutput':repair['gameOutputExisted'] is False and repair['at']<g['at'],
      'registrationBeforeOutputs':p['at']<k['at'] and p['at']<g['at'],
      'codeRegisteredBeforeKernel':lock['at']<k['at'],
      'protocolInResults':g['protocolSHA256']==k['protocolSHA256']==sha(HERE/'protocol.json'),
      'kernelCases19':len(k['kernels'])==19,
      'kernelProbabilityConservation':all(abs(sum(x['exact']['offIndividual'])+sum(x['exact']['defIndividual'])-1)<1e-12 for x in k['kernels']),
      'kernelFiniteNonnegative':all(math.isfinite(y) and 0<=y<=1 for x in k['kernels'] for y in x['exact']['offIndividual']+x['exact']['defIndividual']),
      'samplingOneRecipient':all(sum(s['counts'])==p['opportunitiesPerSeed'] for x in k['kernels'] for s in x['seedRows']),
      'all20Seeds':all([s['seed'] for s in x['seedRows']]==p['seeds'] for x in k['kernels']),
      'gameCount140':len(g['games'])==g['totalGames']==140,
      'gameComplete':all(x['complete'] for x in g['games']),
      'gameLedger':all(x['chances']==x['recovered']==x['terminal'] for x in g['games']),
      'replayNoOrphanRecovery':all(x['orphan']==0 for x in g['games']),
      'replayMissAccounting':all(x['terminal']+x['unresolved']==x['fgMisses']+x['ftMisses'] for x in g['games']),
      'ignoredFieldFullGameParity':not g['parityMismatchSeeds']['boxOutHigh'] and not g['parityMismatchSeeds']['distanceFar'],
      'hustleCreditSanity':all(not x['invalid'] for x in read(HERE/'hustle-summary.json')['rows']),
      'reportExists':(HERE/'report.md').is_file(),
      'hustleImperfectionsDisclosed':(HERE/'hustle-quality-supplement.json').is_file()}
    out={'at':datetime.now(timezone.utc).isoformat(),'pass':all(checks.values()),'checks':checks,
      'protectedFiles':len(before),'changedProtectedFiles':changed,'newProtectedFiles':new,
      'inputCount':len(p['inputHashes']),'protocolSHA256':sha(HERE/'protocol.json'),
      'artifactHashes':{f.name:sha(f) for f in HERE.iterdir() if f.is_file() and f.name!='completion-audit.json'}}
    dump(HERE/'completion-audit.json',out)
    print({'pass':out['pass'],'checks':len(checks),'protectedFiles':len(before),'changed':len(changed),'newProtected':len(new)})
    assert out['pass'],{key:value for key,value in checks.items() if not value}

if __name__=='__main__':
    main()
