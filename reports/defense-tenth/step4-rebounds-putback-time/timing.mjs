import {continuousDuration} from '../../../src/defense_fourth_effects.js';
export function putbackDuration(cdf,clock,shotClock,rng){if(!Array.isArray(cdf)||!cdf.length)throw Error('Missing preregistered putback CDF');const limit=Math.min(14,clock/10-.1,shotClock/10-.1);return Math.max(1,Math.min(continuousDuration(cdf,limit,rng)*10,clock-1,shotClock-1));}
