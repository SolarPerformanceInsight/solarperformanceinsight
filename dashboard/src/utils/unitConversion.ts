import { getVariableUnits } from "@/utils/units.ts";

const powerUnitValues: Record<string, number> = {
  W: 1,
  kW: 1000,
  MW: 1000000,
  GW: 1000000000
};

const energyUnitValues: Record<string, number> = {
  Wh: 1,
  kWh: 1000,
  MWh: 1000000,
  GWh: 1000000000
};

const insolationUnitValues: Record<string, number> = {
  "W/m^2": 1,
  "kW/m^2": 1000,
  "MW/m^2": 1000000,
  "GW/m^2": 1000000000
};

function getUnitValues(units: string) {
  if (units in powerUnitValues) {
    return powerUnitValues;
  } else if (units in energyUnitValues) {
    return energyUnitValues;
  } else if (units in insolationUnitValues) {
    return insolationUnitValues;
  } else {
    return {};
  }
}

export function getUnitConverter(origUnits: string, targetUnits: string) {
  if (origUnits == targetUnits) {
    return null;
  }
  const unitValues: Record<string, number> = getUnitValues(origUnits);
  if (!(targetUnits in unitValues)) {
    return null;
  }
  const orig = unitValues[origUnits];
  const target = unitValues[targetUnits];
  const factor = orig / target;
  return (value: number) => value * factor;
}

export function getUnitOptions(variable: string) {
  const defaultUnits = getVariableUnits(variable);
  return Object.keys(getUnitValues(defaultUnits));
}
