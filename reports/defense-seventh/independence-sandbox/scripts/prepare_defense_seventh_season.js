// Parameterized copies of audited reconstruction programs; no fitting/tuning.
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {hash} from './defense_io.js';
const season=process.argv[2]??'2024-25',data=`data/defense-seventh/${season}`,report=`reports/defense-seventh/${season}/stints`;fs.mkdirSync(report,{recursive:true});
const replacements={'data/defense-a-source/pbp/':data+'/pbp/','data/defense-a-source/manifest.json':data+'/manifest.json','data/defense-source/game-exposure.json':data+'/game-exposure.json','data/defense-source/boxes/':data+'/boxes/','data/season-source/team-games.json':data+'/team-games.json','data/season-league.json':data+'/league.json','reports/defense-b1':report};
const generated=[];
for(const name of ['prepare_defense_b1','validate_defense_stints','prepare_defense_stint_zones']){
 let source=fs.readFileSync('scripts/'+name+'.js','utf8');for(const[a,b]of Object.entries(replacements))source=source.replaceAll(a,b);const file='scripts/.seventh-'+season+'-'+name+'.js';fs.writeFileSync(file,source);generated.push({original:'scripts/'+name+'.js',originalHash:hash('scripts/'+name+'.js'),generated:file,generatedHash:hash(file)});execFileSync(process.execPath,[file],{stdio:'inherit'});
}
fs.writeFileSync(report+'/reconstruction-code.json',JSON.stringify({season,replacements,generated},null,2)+'\n');
