/* Provides a centralized index for producing unique index values. Useful for
 * creating unique ids for inputs and labels e.g. field-1, field-title-1,
 * field-help-1
 */
let index = 1;

export function getIndex() {
  const current = index;
  index++;
  return current;
}

export function resetIndex() {
  index = 1;
}
