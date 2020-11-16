export class PVSystTemperatureParameters {
  /* Currently only supports pvsyst model */
  uC: number; // pvlib "Freestanding" default insulated is 15.0
  uV: number; //        freestanding:00, insulated: 0.0

  constructor({ uC = 29.0, uV = 0.0 } = {}) {
    this.uC = uC;
    this.uV = uV;
  }
}

export class PVWattsTemperatureParameters {
  a: number;
  b: number;
  deltaT: number;

  constructor({ a = 0, b = 0, deltaT = 0 } = {}) {
    this.a = a;
    this.b = b;
    this.deltaT = deltaT;
  }
}
