interface ModelSpec {
  transposition_model: string;
  dc_model: string;
  ac_model: string;
  aoi_model: string;
  spectral_model: string;
  temperature_model: string;
  clearsky_model: string;
  airmass_model: string;
  losses_model: string;
}

interface SpecCollection {
  [key: string]: ModelSpec;
}

export const modelSpecs: SpecCollection = {
  pvsyst: {
    transposition_model: "haydavies",
    dc_model: "pvsyst",
    ac_model: "sandia",
    aoi_model: "physical",
    spectral_model: "no_loss",
    temperature_model: "pvsyst",
    clearsky_model: "ineichen",
    airmass_model: "kastenyoung1989",
    losses_model: "no_loss"
  },
  pvwatts: {
    transposition_model: "perez",
    dc_model: "pvwatts",
    ac_model: "pvwatts",
    aoi_model: "physical",
    spectral_model: "no_loss",
    temperature_model: "sapm",
    clearsky_model: "ineichen",
    airmass_model: "kastenyoung1989",
    losses_model: "pvwatts"
  },
  sam: {
    transposition_model: "haydavies",
    dc_model: "pvsyst",
    ac_model: "sandia",
    aoi_model: "physical",
    spectral_model: "no_loss",
    temperature_model: "pvsyst",
    clearsky_model: "ineichen",
    airmass_model: "kastenyoung1989",
    losses_model: "no_loss"
  }
};
