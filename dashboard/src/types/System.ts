import { Inverter } from "./Inverter";

export class System {
  name: string;
  latitude: number;
  longitude: number;
  elevation: number;
  albedo: number;
  inverters: Inverter[];

  constructor({
    name = "New System",
    latitude = 0,
    longitude = 0,
    elevation = 0,
    albedo = 0,
    inverters = []
  }: Partial<System>) {
    this.name = name;
    this.latitude = latitude;
    this.longitude = longitude;
    this.elevation = elevation;
    this.albedo = albedo;
    if (inverters.length == 0) {
      this.inverters = [];
    } else {
      this.inverters = inverters.map(i => new Inverter(i));
    }
  }
  static isInstance(obj: any): obj is System {
    const maybe = obj as System;
    return (
      maybe.name != undefined &&
      maybe.latitude != undefined &&
      maybe.longitude != undefined &&
      maybe.elevation != undefined &&
      maybe.albedo != undefined &&
      maybe.inverters != undefined
    );
  }
}
