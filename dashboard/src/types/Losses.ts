export class PVWattsLosses {
  soiling: number;
  shading: number;
  snow: number;
  mismatch: number;
  wiring: number;
  connections: number;
  lid: number;
  nameplate_rating: number;
  age: number;
  availability: number;

  constructor({
    soiling = 2.0,
    shading = 3.0,
    snow = 0.0,
    mismatch = 2.0,
    wiring = 2.0,
    connections = 0.5,
    lid = 1.5,
    nameplate_rating = 1.0,
    age = 0.0,
    availability = 3.0
  }: Partial<PVWattsLosses>) {
    this.soiling = soiling;
    this.shading = shading;
    this.snow = snow;
    this.mismatch = mismatch;
    this.wiring = wiring;
    this.connections = connections;
    this.lid = lid;
    this.nameplate_rating = nameplate_rating;
    this.age = age;
    this.availability = availability;
  }
  static isInstance(obj: any): obj is PVWattsLosses {
    const maybe = obj as PVWattsLosses;
    return (
      maybe.soiling != undefined &&
      maybe.shading != undefined &&
      maybe.snow != undefined &&
      maybe.mismatch != undefined &&
      maybe.wiring != undefined &&
      maybe.connections != undefined &&
      maybe.lid != undefined &&
      maybe.nameplate_rating != undefined &&
      maybe.age != undefined &&
      maybe.availability != undefined
    );
  }
}
