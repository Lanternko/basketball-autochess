import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v24/input.mjs';
const cache=new Map(),read=f=>JSON.parse(fs.readFileSync(f));
export function contactSource(season){if(!cache.has(season))cache.set(season,{source:read(`reports/player-impact-v25/${season}-contact-policy.json`),recipient:read(`reports/player-impact-v25/${season}-contact-recipient.json`)});return cache.get(season);}
export function attachContact(players,season){const src=contactSource(season);for(const p of players){const m=src.recipient.cards[p.playerId];if(!m)throw Error('Missing source contact recipient');p.contactRecipientMeasurement={...m,source:'Conditional ordinary defensive nonshooting personal-contact victim allocation given actual five. Relative source production/style, not causal foul-drawing skill; zero-centered prior chooses disconnected-team scale.'};}return players;}
export function ordinaryContactReference(season){
 const src=contactSource(season).source,c=src.groups.ordinary,n=c.nonshootingContact,terminal=c.fga+c.tov+c.unrecordedShootingFouls,multi=src.counts.multipleShotMatches??0;
 return {rate:n/(n+terminal+multi),upper:n/(n+terminal),ordinaryContacts:n,ordinaryTerminal:terminal,conservativeExtraShootingFouls:multi,sourcePolicy:'Exclude source action-time endgame eligibility from ordinary contact rate; keep engine forced endgame policy unchanged. Source event clock differs from pre-setup touch clock, retained policy approximation.'};
}
export function loadInput(season){const b=previousInput(season);attachContact(b.league.teams.flatMap(t=>t.roster),season);b.ordinaryContactReference=ordinaryContactReference(season);b.options.nonShootingFoulRate=b.ordinaryContactReference.rate;return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachContact(players,season);}
