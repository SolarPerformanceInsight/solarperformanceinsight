import { PVArray } from "./PVArray";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "./InverterParameters";
import { PVWattsLosses } from "./Losses";

export class Inverter {
  name: string;
  make_model: string;
  inverter_parameters: SandiaInverterParameters | PVWattsInverterParameters;
  losses?: PVWattsLosses;
  arrays: Array<PVArray>;

  constructor({
    name = "",
    make_model = "",
    inverter_parameters = new SandiaInverterParameters({}),
    arrays = [],
    losses
  }: Partial<Inverter>) {
    this.name = name;
    this.make_model = make_model;
    if (PVWattsInverterParameters.isInstance(inverter_parameters)) {
      this.inverter_parameters = new PVWattsInverterParameters(
        inverter_parameters
      );
    } else {
      this.inverter_parameters = new SandiaInverterParameters(
        inverter_parameters
      );
    }
    if (PVWattsLosses.isInstance(losses)) {
      this.losses = new PVWattsLosses(losses);
    } //
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
      maybe.arrays != undefined
    );
  }
}
