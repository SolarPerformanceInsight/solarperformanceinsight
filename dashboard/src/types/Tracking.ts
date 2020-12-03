export class FixedTrackingParameters {
  tilt: number;
  azimuth: number;

  constructor({ tilt = 0, azimuth = 0 }: Partial<FixedTrackingParameters>) {
    this.tilt = tilt;
    this.azimuth = azimuth;
  }
  static isInstance(obj: any): obj is FixedTrackingParameters {
    const maybe = obj as FixedTrackingParameters;
    return maybe.tilt !== undefined && maybe.azimuth !== undefined;
  }
}

export class SingleAxisTrackingParameters {
  axis_tilt: number;
  axis_azimuth: number;
  gcr: number;
  backtracking: boolean;

  constructor({
    axis_tilt = 0,
    axis_azimuth = 0,
    gcr = 0,
    backtracking = false
  }: Partial<SingleAxisTrackingParameters>) {
    this.axis_tilt = axis_tilt;
    this.axis_azimuth = axis_azimuth;
    this.gcr = gcr;
    this.backtracking = backtracking;
  }
  static isInstance(obj: any): obj is SingleAxisTrackingParameters {
    const maybe = obj as SingleAxisTrackingParameters;
    return (
      maybe.axis_tilt !== undefined &&
      maybe.axis_azimuth !== undefined &&
      maybe.gcr !== undefined &&
      maybe.backtracking !== undefined
    );
  }
}
