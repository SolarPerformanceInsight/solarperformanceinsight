const unitValues: Record<string, number> = {
  W: 1,
  kW: 1000,
  MW: 1000000,
  GW: 1000000000,
}

export default function convertPower(
  origUnits: string,
  targetUnits: string,
  value: number
) {
  const orig = unitValues[origUnits];
  const target = unitValues[targetUnits];
  const factor = orig / target;
  return value * factor;
}
