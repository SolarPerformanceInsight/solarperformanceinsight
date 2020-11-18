export class PVSystTemperatureParameters {
  /* Currently only supports pvsyst model */
  uC: number; // pvlib "Freestanding" default insulated is 15.0
  uV: number; //        freestanding:00, insulated: 0.0

  constructor({ uC = 29.0, uV = 0.0 } = {}) {
    this.uC = uC;
    this.uV = uV;
  }
  static isInstance(obj: any): obj is PVSystTemperatureParameters {
      let maybe = obj as PVSystTemperatureParameters;
      return maybe.uC != undefined
             && maybe.uV != undefined;
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
  static isInstance(obj: any): obj is PVWattsTemperatureParameters {
      let maybe = obj as PVWattsTemperatureParameters;
      return maybe.a != undefined
             && maybe.b != undefined
             && maybe.deltaT != undefined;
  }
}
