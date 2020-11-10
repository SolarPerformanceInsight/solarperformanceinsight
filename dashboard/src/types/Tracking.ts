export class FixedTrackingParameters {
  tilt: number;
  azimuth: number;

  constructor({ tilt = 0, azimuth = 0 } = {}) {
    this.tilt = tilt;
    this.azimuth = azimuth;
  }
}

export class SingleAxisTrackingParameters {
  axis_tilt: number;
  axis_azimuth: number;
  gcr: number;

  constructor({ axis_tilt = 0, axis_azimuth = 0, gcr = 0 } = {}) {
    this.axis_tilt = axis_tilt;
    this.axis_azimuth = axis_azimuth;
    this.gcr = gcr;
  }
}
