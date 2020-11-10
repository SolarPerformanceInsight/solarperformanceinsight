export class FixedTrackingParameters {
  tilt: number;
  azimuth: number;

  constructor({ tilt = 0, azimuth = 0 } = {}) {
    this.tilt = tilt;
    this.azimuth = azimuth;
  }
}

export class SingleAxisTrackingParameters {
  axisTilt: number;
  axisAzimuth: number;
  gcr: number;

  constructor({ axisTilt = 0, axisAzimuth = 0, gcr = 0 } = {}) {
    this.axisTilt = axisTilt;
    this.axisAzimuth = axisAzimuth;
    this.gcr = gcr;
  }
}
