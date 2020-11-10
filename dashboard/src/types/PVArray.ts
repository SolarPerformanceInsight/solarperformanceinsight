import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "./Tracking";
import { PvsystTemperatureParameters } from "./TemperatureParameters";
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "./ModuleParameters";

export class PVArray {
  name: string;
  make_model: string;
  module_parameters: PVSystModuleParameters | PVWattsModuleParameters;
  temperature_model_parameters: Array<number> | PvsystTemperatureParameters;
  tracking: FixedTrackingParameters | SingleAxisTrackingParameters;
  // PVSyst parameters
  modules_per_string: number;
  strings: number;
  losses_parameters: any;

  constructor({
    name = "New Array",
    make_model = "ABC 123",
    module_parameters = new PVSystModuleParameters(),
    temperature_model_parameters = [],
    tracking = new FixedTrackingParameters(),
    modules_per_string = 0,
    strings = 0,
    losses_parameters = {}
  } = {}) {
    this.name = name;
    this.make_model = make_model;
    this.modules_per_string = modules_per_string;
    this.strings = strings;
    this.losses_parameters = losses_parameters;

    if (module_parameters instanceof PVWattsModuleParameters) {
      this.module_parameters = new PVWattsModuleParameters(module_parameters);
    } else {
      this.module_parameters = new PVSystModuleParameters(module_parameters);
    }

    if (tracking instanceof FixedTrackingParameters) {
      this.tracking = new FixedTrackingParameters(tracking);
    } else {
      this.tracking = new SingleAxisTrackingParameters(tracking);
    }

    if (temperature_model_parameters instanceof PvsystTemperatureParameters) {
      this.temperature_model_parameters = new PvsystTemperatureParameters(
        temperature_model_parameters
      );
    } else {
      this.temperature_model_parameters = temperature_model_parameters;
    }
  }
}
