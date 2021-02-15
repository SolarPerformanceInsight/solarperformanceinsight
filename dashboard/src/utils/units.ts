// TODO: Fix
export const variableUnits: Record<string, string> = {
  time: "Timestamp",
  ghi: "W/m^2",
  dhi: "W/m^2",
  dni: "W/m^2",
  poa_global: "W/m^2",
  poa_diffuse: "W/m^2",
  poa_direct: "W/m^2",
  effective_irradiance: "W/m^2",
  cell_temperature: "C",
  module_temperature: "C",
  temp_air: "C",
  wind_speed: "m/s",
  performance: "W",
  daytime_flag: "Flag", // fix below
  total_energy: "Total Energy",
  plane_of_array_insolation: "Plane of Array Insolation",
  effective_insolation: "Effective Insolation",
  average_daytime_cell_temperature: "Average Daytime Cell Temperature",
  month: "Month"
};

export function getVariableUnits(variable: string) {
  const variableName = variableUnits[variable];
  if (variableName) {
    return variableName;
  } else {
    console.error(`Could not find units for ${variable}.`);
    return variable;
  }
}
