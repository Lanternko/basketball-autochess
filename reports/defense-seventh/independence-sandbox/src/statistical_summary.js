export const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
export const variance=xs=>{const center=mean(xs);return mean(xs.map(v=>(v-center)**2));};
export const sd=xs=>Math.sqrt(variance(xs));
