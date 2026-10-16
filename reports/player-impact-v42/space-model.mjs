import {spaceProbability as previousSpace} from '../player-impact-v22/model.mjs';
import {applyRecordedZone} from './choice-model.mjs';
export function spaceProbability(p,player,putback,opt){
 const q=previousSpace(p,player,putback,opt);
 return putback?q:applyRecordedZone(q,p.defensiveZone);
}
