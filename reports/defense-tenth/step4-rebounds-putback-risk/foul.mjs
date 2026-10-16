export function isNonShooting(e){
 const text=[e.subType,e.descriptor,...(e.qualifiers??[])].join(' ');
 return !/shooting|offensive|technical|flagrant|clearpath|awayfromplay|transition[\s-]?take/i.test(text);
}
