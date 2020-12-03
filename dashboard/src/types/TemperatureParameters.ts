export class PVSystTemperatureParameters {
  /* Currently only supports pvsyst model */
  u_c: number; // pvlib "Freestanding" default insulated is 15.0
  u_v: number; //        freestanding:00, insulated: 0.0
  eta_m: number;
  alpha_absorption: number;

  constructor({
    u_c = 29.0,
    u_v = 0.0,
    eta_m = 0.1,
    alpha_absorption = 0.9
  }: Partial<PVSystTemperatureParameters>) {
    this.u_c = u_c;
    this.u_v = u_v;
    this.eta_m = eta_m;
    this.alpha_absorption = alpha_absorption;
  }
  static isInstance(obj: any): obj is PVSystTemperatureParameters {
    const maybe = obj as PVSystTemperatureParameters;
    return maybe.u_c != undefined && maybe.u_v != undefined;
  }
}

export class SAPMTemperatureParameters {
  a: number;
  b: number;
  deltaT: number;

  constructor({
    a = 0,
    b = 0,
    deltaT = 0
  }: Partial<SAPMTemperatureParameters>) {
    this.a = a;
    this.b = b;
    this.deltaT = deltaT;
  }
  static isInstance(obj: any): obj is SAPMTemperatureParameters {
    const maybe = obj as SAPMTemperatureParameters;
    return (
      maybe.a != undefined && maybe.b != undefined && maybe.deltaT != undefined
    );
  }
}
