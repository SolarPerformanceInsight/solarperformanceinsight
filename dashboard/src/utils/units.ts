export const variableUnits: Record<string, string> = {
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
  daytime_flag: "True/False",
  total_energy: "Wh",
  plane_of_array_insolation: "Wh/m^2",
  total_poa_insolation: "Wh/m^2",
  effective_insolation: "Wh/m^2",
  average_daytime_cell_temperature: "C",
  actual_energy: "Wh",
  modeled_energy: "Wh",
  difference: "Wh",
  ratio: "%",
  weather_adjusted_energy: "Wh"
};

const unitless = ["time", "month"];
export function getVariableUnits(variable: string) {
  if (unitless.includes(variable)) {
    return "";
  }
  const variableName = variableUnits[variable];
  if (variableName) {
    return variableName;
  } else {
    console.error(`Could not find units for ${variable}.`);
    return "";
  }
}
