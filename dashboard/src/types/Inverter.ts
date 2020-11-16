import { PVArray } from "./PVArray";
import {
  PVSystInverterParameters,
  PVWattsInverterParameters
} from "./InverterParameters";

export class Inverter {
  name: string;
  make_model: string;
  inverter_parameters: PVSystInverterParameters | PVWattsInverterParameters;
  losses_parameters: any;
  arrays: Array<PVArray>;

  constructor({
    name = "New Inverter",
    make_model = "ABC 520",
    inverter_parameters = new PVSystInverterParameters(),
    losses_parameters = {},
    arrays = []
  } = {}) {
    this.name = name;
    this.make_model = make_model;
    this.inverter_parameters = inverter_parameters;
    this.losses_parameters = losses_parameters;

    if (arrays.length == 0) {
      this.arrays = [];
    } else {
      this.arrays = arrays.map(a => new PVArray(a));
    }
  }
}
