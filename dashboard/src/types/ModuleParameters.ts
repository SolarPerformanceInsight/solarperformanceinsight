export class PVSystModuleParameters {
  alpha_sc: number;
  gamma_ref: number;
  mu_gamma: number;
  I_L_ref: number;
  I_o_ref: number;
  R_sh_ref: number;
  R_sh_0: number;
  R_s: number;
  cells_in_series: number;
  R_sh_exp: number;
  EgRef: number;

  constructor({
    alpha_sc = 0,
    gamma_ref = 0,
    mu_gamma = 0,
    I_L_ref = 0,
    I_o_ref = 0,
    R_sh_ref = 0,
    R_sh_0 = 0,
    R_s = 0,
    cells_in_series = 0,
    R_sh_exp = 5.5,
    EgRef = 1.121
  }: Partial<PVSystModuleParameters>) {
    this.alpha_sc = alpha_sc;
    this.gamma_ref = gamma_ref;
    this.mu_gamma = mu_gamma;
    this.I_L_ref = I_L_ref;
    this.I_o_ref = I_o_ref;
    this.R_sh_ref = R_sh_ref;
    this.R_sh_0 = R_sh_0;
    this.R_s = R_s;
    this.EgRef = EgRef;
    this.cells_in_series = cells_in_series;
    this.R_sh_exp = R_sh_exp;
  }

  static isInstance(obj: any): obj is PVSystModuleParameters {
    const maybe = obj as PVSystModuleParameters;
    return (
      maybe.alpha_sc != undefined &&
      maybe.gamma_ref != undefined &&
      maybe.mu_gamma != undefined &&
      maybe.I_L_ref != undefined &&
      maybe.I_o_ref != undefined &&
      maybe.R_sh_ref != undefined &&
      maybe.R_sh_0 != undefined &&
      maybe.R_s != undefined &&
      maybe.EgRef != undefined &&
      maybe.cells_in_series != undefined &&
      maybe.R_sh_exp != undefined
    );
  }
}

export class PVWattsModuleParameters {
  pdc0: number;
  gamma_pdc: number;

  constructor({ pdc0 = 0, gamma_pdc = 0 }: Partial<PVWattsModuleParameters>) {
    this.pdc0 = pdc0;
    this.gamma_pdc = gamma_pdc;
  }
  static isInstance(obj: any): obj is PVWattsModuleParameters {
    const maybe = obj as PVWattsModuleParameters;
    return maybe.pdc0 != undefined && maybe.gamma_pdc != undefined;
  }
}
export class CECModuleParameters {
  alpha_sc: number;
  a_ref: number;
  I_L_ref: number;
  I_o_ref: number;
  R_sh_ref: number;
  R_s: number;
  cells_in_series: number;
  Adjust: number;
  EgRef: number;
  dEgdT: number;

  constructor({
    alpha_sc = 0,
    a_ref = 0,
    I_L_ref = 0,
    I_o_ref = 0,
    R_sh_ref = 0,
    R_s = 0,
    cells_in_series = 0,
    Adjust = 0,
    EgRef = 1.121,
    dEgdT = -0.0002677
  }: Partial<CECModuleParameters>) {
    this.alpha_sc = alpha_sc;
    this.a_ref = a_ref;
    this.I_L_ref = I_L_ref;
    this.I_o_ref = I_o_ref;
    this.R_sh_ref = R_sh_ref;
    this.R_s = R_s;
    this.cells_in_series = cells_in_series;
    this.Adjust = Adjust;
    this.EgRef = EgRef;
    this.dEgdT = dEgdT;
  }
  static isInstance(obj: any): obj is CECModuleParameters {
    const maybe = obj as CECModuleParameters;
    return (
      maybe.alpha_sc != undefined &&
      maybe.a_ref != undefined &&
      maybe.I_L_ref != undefined &&
      maybe.I_o_ref != undefined &&
      maybe.R_sh_ref != undefined &&
      maybe.R_s != undefined &&
      maybe.cells_in_series != undefined &&
      maybe.Adjust != undefined &&
      maybe.EgRef != undefined &&
      maybe.dEgdT != undefined
    );
  }
}
