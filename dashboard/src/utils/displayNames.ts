/* collection of objects mapping native variables to display names */
export const variableDisplayNames: Record<string, string> = {
  time: "Timestamp",
  ghi: "Global Horizontal Irradiance",
  dhi: "Diffuse Horizontal Irradiance",
  dni: "Direct Normal Irradiance",
  poa_global: "Plane of Array Global Irradiance",
  poa_diffuse: "Plane of Array Diffuse Irradiance",
  poa_direct: "Plane of Array Direct Irradiance",
  effective_irradiance: "Effective Irradiance",
  cell_temperature: "Cell Temperature",
  module_temperature: "Module Temperature",
  temp_air: "Air Temperature",
  wind_speed: "Wind Speed",
  performance: "Performance (AC power)",
  daytime_flag: "Daytime Flag",
  total_energy: "Total Energy",
  plane_of_array_insolation: "Plane of Array Insolation",
  effective_insolation: "Effective Insolation",
  average_daytime_cell_temperature: "Average Daytime Cell Temperature",
  month: "Month"
};

export function getVariableDisplayName(variable: string) {
  const variableName = variableDisplayNames[variable];
  if (variableName) {
    return variableName;
  } else {
    console.error(`Could not find ${variable} in variableDisplayNames`);
    return variable;
  }
}
