import { Inverter } from "./Inverter";

export class System {
  name: string;
  latitude: number;
  longitude: number;
  elevation: number;
  inverters: Inverter[];

  constructor({
    name = "New System",
    latitude = 0,
    longitude = 0,
    elevation = 0,
    inverters = []
  }: Partial<System>) {
    this.name = name;
    this.latitude = latitude;
    this.longitude = longitude;
    this.elevation = elevation;
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
      maybe.inverters != undefined
    );
  }
}
export class StoredSystem {
  object_id!: string;
  object_type = "system";
  created_at!: string;
  modified_at!: string;
  definition!: System;

  constructor(stored: StoredSystem) {
    this.object_id = stored.object_id;
    this.created_at = stored.created_at;
    this.modified_at = stored.modified_at;
    this.definition = new System(stored.definition);
  }
}
