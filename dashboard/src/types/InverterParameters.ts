export class PVSystInverterParameters {
  /* Class mimics the inverter parameters required for the pvsyst model
   * provided by the PVLib inverter database.
   * See: https://github.com/pvlib/pvlib-python/blob/3e25627e34bfd5aadea041da85a30626322b3a99/pvlib/pvsystem.py#L1355
   */
  Paco: number; //AC power rating of the inverter. [W]
  Pdco: number; //DC power input to inverter, typically assumed to be equal
  //to the PV array maximum power. [W]
  Vdco: number; //DC voltage at which the AC power rating is achieved
  //at the reference operating condition. [V]
  Pso: number; //DC power required to start the inversion process, or
  //self-consumption by inverter, strongly influences inverter
  //efficiency at low power levels. [W]
  C0: number; //Parameter defining the curvature (parabolic) of the
  //relationship between AC power and DC power at the reference
  //operating condition. [1/W]
  C1: number; //Empirical coefficient allowing ``Pdco`` to vary linearly
  //with DC voltage input. [1/V]
  C2: number; //Empirical coefficient allowing ``Pso`` to vary linearly with
  //DC voltage input. [1/V]
  C3: number; //Empirical coefficient allowing ``C0`` to vary linearly with
  //DC voltage input. [1/V]
  Pnt: number; //AC power consumed by the inverter at night (night tare). [W]

  // TODO: fix defaults?
  constructor({
    Paco = 0,
    Pdco = 0,
    Vdco = 0,
    Pso = 0,
    C0 = 0,
    C1 = 0,
    C2 = 0,
    C3 = 0,
    Pnt = 0
  }: Partial<PVSystInverterParameters>) {
    this.Paco = Paco;
    this.Pdco = Pdco;
    this.Vdco = Vdco;
    this.Pso = Pso;
    this.C0 = C0;
    this.C1 = C1;
    this.C2 = C2;
    this.C3 = C3;
    this.Pnt = Pnt;
  }

  static isInstance(obj: any): obj is PVSystInverterParameters {
    const maybe = obj as PVSystInverterParameters;
    return (
      maybe.Paco != undefined &&
      maybe.Pdco != undefined &&
      maybe.Vdco != undefined &&
      maybe.Pso != undefined &&
      maybe.C0 != undefined &&
      maybe.C1 != undefined &&
      maybe.C2 != undefined &&
      maybe.C3 != undefined &&
      maybe.Pnt != undefined
    );
  }

  static fromPvlibDb() {
    return new PVSystInverterParameters({});
  }
}

export class PVWattsInverterParameters {
  pdc: number;
  pdc0: number;
  eta_inv_nom: number;
  eta_inv_ref: number;

  constructor({
    pdc = 0,
    pdc0 = 0,
    eta_inv_nom = 0.96,
    eta_inv_ref = 0.9637
  }: Partial<PVWattsInverterParameters>) {
    this.pdc = pdc;
    this.pdc0 = pdc0;
    this.eta_inv_nom = eta_inv_nom;
    this.eta_inv_ref = eta_inv_ref;
  }
  static isInstance(obj: any): obj is PVWattsInverterParameters {
    const maybe = obj as PVWattsInverterParameters;
    return (
      maybe.pdc !== undefined &&
      maybe.pdc0 !== undefined &&
      maybe.eta_inv_nom != undefined &&
      maybe.eta_inv_ref != undefined
    );
  }
}
