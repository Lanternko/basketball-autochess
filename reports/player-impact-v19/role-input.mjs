import fs from 'node:fs';
import {loadInput as previousInput,attachCreationRates as previousRates} from '../player-impact-v18/role-input.mjs';
import {attachFreeThrowProfilePrior} from '../../src/free_throw_profile_prior.js';
export {attachShooting} from '../player-impact-v9/input.mjs';
function attachShootingFtr(players,season){
 const fit=JSON.parse(fs.readFileSync('reports/player-impact-v19/ftr-prior.json'));
 attachFreeThrowProfilePrior(players,fit.references[season],fit.kappaFga);
 for(const p of players){const m=p.freeThrowProfileMeasurement;m.fullSeasonMinutes=m.minutes;delete m.minutes;
  m.source='Strict PBP classified SHOOTING FTA per recorded FGA; full-season MIN is metadata only. Common prior fitted on five game folds in2022-25. Technical/nonshooting/unresolved FTA excluded from shooting target. Raw drive attribute unchanged.';m.freeThrowScope='shooting-only';}
 return players;
}
export function attachCreationRates(players,season){previousRates(players,season);return attachShootingFtr(players,season);}
export function loadInput(season){const b=previousInput(season);attachShootingFtr(b.league.teams.flatMap(t=>t.roster),season);
 const contact=JSON.parse(fs.readFileSync(`reports/player-impact-v19/${season}-foul-contact-audit.json`));
 if(contact.missingDrawnShooter)throw Error('Source shooting-contact denominator needs unresolved linkage audit');
 b.options.nonShootingFoulRate=contact.nonshootingContactRateBounds.lower;b.nonshootingContactReference={...contact.nonshootingContactRateBounds,policy:"Conservative contact probability: every multi-FGA clock match may add an unrecorded terminal shooting foul."};return b;
}
