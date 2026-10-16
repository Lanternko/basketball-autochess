// v53 = v47 probabilities plus dead-ball pressure from the defending five (pressure.mjs).
// Terminal signature: (handler, ctx, defender, help, oreb, dreb, phys, opts, lineup, opt).
import {terminalDefenseProbabilities as previousTerminal, exposureDefenseProbabilities} from '../player-impact-v47/model.mjs';
import {withDeadBallPressure} from './pressure.mjs';
export {exposureDefenseProbabilities};
export function terminalDefenseProbabilities(handler, ctx, defender, help, oreb, dreb, phys, opts, lineup, opt) {
  const q = previousTerminal(handler, ctx, defender, help, oreb, dreb, phys, opts, lineup, opt);
  return opts?.putback ? q : withDeadBallPressure(q, lineup);
}
