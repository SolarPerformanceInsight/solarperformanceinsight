import { Inverter } from "./Inverter";

export class System {
  name: string;
  latitude: number;
  longitude: number;
  elevation: number;
  albedo: number;
  inverters: Array<Inverters>;

  constructor({
    name = "New System",
    latitude = 0,
    longitude = 0,
    elevation = 0,
    albedo = 0,
    inverters = []
  } = {}) {
    this.name = name;
    this.latitude = latitude;
    this.longitude = longitude;
    this.elevation = elevation;
    this.albedo = albedo;
    if (inverters.length == 0) {
      this.inverters = [new Inverter()];
    } else {
      this.inverters = inverters.map(i => new Inverter(i));
    }
  }
}
