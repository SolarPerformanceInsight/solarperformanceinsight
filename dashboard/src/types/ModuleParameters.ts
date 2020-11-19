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
  }: Partial<PVSystModelingParameters>) {
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
  static isInstance(obj: any): obj is PVSystModuleParameters {
    const maybe = obj as PVSystModuleParameters;
    return (
      maybe.gamma_ref != undefined &&
      maybe.mu_gamma != undefined &&
      maybe.I_L_ref != undefined &&
      maybe.R_sh_ref != undefined &&
      maybe.R_sh_0 != undefined &&
      maybe.R_s != undefined &&
      maybe.alpha_sc != undefined &&
      maybe.EgRef != undefined &&
      maybe.cells_in_series != undefined
    );
  }
}

export class PVWattsModuleParameters {
  pdc0: number;
  gamma_pdc: number;

  constructor({
    pdc0 = 0,
    gamma_pdc = 0
  }: Partial<PVwattsModuleParameters>){
    this.pdc0 = pdc0;
    this.gamma_pdc = gamma_pdc;
  }
  static isInstance(obj: any): obj is PVWattsModuleParameters {
    const maybe = obj as PVWattsModuleParameters;
    return maybe.pdc0 != undefined && maybe.gamma_pdc != undefined;
  }
}
