interface ModelSpec {
  transposition_model: string;
  dc_model: string;
  ac_model: string;
  aoi_model: string;
  spectral_model: string;
  temperature_model: string;
  losses_model: string;
}

interface SpecCollection {
  [key: string]: ModelSpec;
}

export const modelSpecs: SpecCollection = {
  pvsyst: {
    transposition_model: "",
    dc_model: "pvsyst",
    ac_model: "",
    aoi_model: "",
    spectral_model: "",
    temperature_model: "pvsyst",
    losses_model: ""
  },
  pvwatts: {
    transposition_model: "perez",
    dc_model: "pvwatts",
    ac_model: "pvwatts",
    aoi_model: "physical",
    spectral_model: "no_loss",
    temperature_model: "sapm",
    losses_model: "pvwatts"
  }
};
