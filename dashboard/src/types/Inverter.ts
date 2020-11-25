import { PVArray } from "./PVArray";
import {
  PVSystInverterParameters,
  PVWattsInverterParameters
} from "./InverterParameters";
import {
  PVWattsLosses
} from "./Losses";

export class Inverter {
  name: string;
  make_model: string;
  inverter_parameters: PVSystInverterParameters | PVWattsInverterParameters;
  losses: PVWattsLosses | null;
  arrays: Array<PVArray>;

  constructor({
    name = "New Inverter",
    make_model = "ABC 520",
    inverter_parameters = new PVSystInverterParameters({}),
    losses = null,
    arrays = []
  }: Partial<Inverter>) {
    this.name = name;
    this.make_model = make_model;
    if (PVWattsInverterParameters.isInstance(inverter_parameters)) {
      this.inverter_parameters = new PVWattsInverterParameters(
        inverter_parameters
      );
    } else {
      this.inverter_parameters = new PVSystInverterParameters(
        inverter_parameters
      );
    }
    if (PVWattsLosses.isInstance(losses)){
        this.losses = new PVWattsLosses(losses)
    } else {
        this.losses = losses;
    }
    if (arrays.length == 0) {
      this.arrays = [];
    } else {
      this.arrays = arrays.map(a => new PVArray(a));
    }
  }

  static isInstance(obj: any): obj is Inverter {
    const maybe = obj as Inverter;
    return (
      maybe.name != undefined &&
      maybe.make_model != undefined &&
      maybe.inverter_parameters != undefined &&
      maybe.losses != undefined &&
      maybe.arrays != undefined
    );
  }
}
