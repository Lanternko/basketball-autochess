import fs from 'node:fs';
import {read,hash} from './defense_io.js';
export function buildV5(configFile,multiplier,{label='v5',output=null}={}){
 if(!(multiplier>=0&&multiplier<=1))throw Error('Multiplier outside frozen shrink range');
 const original=read(configFile),dir=output??original.root,config=structuredClone(original);fs.mkdirSync(dir,{recursive:true});config.root=dir;
 const m=read(original.root+'/ability-model-forward.json'),scaled=structuredClone(m);scaled.models.role.offenseResidual=scaled.models.role.offenseResidual.map(v=>v*multiplier);
 scaled.eighthResidualScale={multiplier,sourceModel:hash(original.root+'/ability-model-forward.json'),onlyChanged:'models.role.offenseResidual; minutes/prior/defense/intercept unchanged'};
 fs.writeFileSync(dir+'/ability-model-forward.json',JSON.stringify(scaled)+'\n');fs.writeFileSync(dir+'/card-values.json',fs.readFileSync(original.root+'/card-values.json'));fs.writeFileSync(dir+'/bundle.json',fs.readFileSync(original.root+'/bundle.json'));fs.writeFileSync(dir+'/config.json',JSON.stringify(config,null,2)+'\n');
 // New isolated wrapper uses the frozen builder byte-for-byte, with only its
 // exported function name/CLI entry renamed to prevent accidental CLI execution.
 let s=fs.readFileSync('scripts/build_defense_seventh_cards.js','utf8');s=s.replaceAll('buildSeventh','buildEighthProjection').replace("endsWith('build_defense_seventh_cards.js')","endsWith('build_defense_eighth_v5_projection.js')");
 const file=`scripts/.eighth-v5-projection-${hash(configFile).slice(0,12)}-${multiplier.toFixed(6).replace('.','p')}.js`;fs.writeFileSync(file,s);
 return import(new URL('../'+file,import.meta.url)).then(({buildEighthProjection})=>{
  buildEighthProjection(original.k,{label,configFile:dir+'/config.json'});
  const leagueFile=dir+`/pre${original.k}-${label}-league.json`,league=read(leagueFile);league.eighthProvenance={workflow:'v5',multiplier,sourceModel:scaled.eighthResidualScale.sourceModel,sourceBuilder:hash('scripts/build_defense_seventh_cards.js'),intervention:'Role offense residual only, prior and defense unchanged'};
  fs.writeFileSync(leagueFile,JSON.stringify(league)+'\n');return {configFile:dir+'/config.json',cardFile:leagueFile,dir,multiplier};
 });
}
if(process.argv[1]?.endsWith('build_defense_eighth_v5_cards.js'))await buildV5(process.argv[2],Number(process.argv[3]),{output:process.argv[4]});
