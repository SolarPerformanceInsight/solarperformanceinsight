export class PVSystModuleParameters {
  gamma_ref: number;
  mu_gamma: number;
  I_L_ref: number;
  I_o_ref: number;
  R_sh_ref: number;
  R_sh_0: number;
  R_s: number;
  alpha_sc: number;
  EgRef: number;
  cells_in_series: number;

  constructor({
    gamma_ref = 0,
    mu_gamma = 0,
    I_L_ref = 0,
    I_o_ref = 0,
    R_sh_ref = 0,
    R_sh_0 = 0,
    R_s = 0,
    alpha_sc = 0,
    EgRef = 0,
    cells_in_series = 0
  } = {}) {
    this.gamma_ref = gamma_ref;
    this.mu_gamma = mu_gamma;
    this.I_L_ref = I_L_ref;
    this.I_o_ref = I_o_ref;
    this.R_sh_ref = R_sh_ref;
    this.R_sh_0 = R_sh_0;
    this.R_s = R_s;
    this.alpha_sc = alpha_sc;
    this.EgRef = EgRef;
    this.cells_in_series = cells_in_series;
  }
}

export class PVWattsModuleParameters {
  pdc0: number;
  gamma_pdc: number;

  constructor({ pdc0 = 0, gamma_pdc = 0 } = {}) {
    this.pdc0 = pdc0;
    this.gamma_pdc = gamma_pdc;
  }
}
