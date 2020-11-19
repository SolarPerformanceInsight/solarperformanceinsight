import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "./Tracking";
import {
  PVSystTemperatureParameters,
  PVWattsTemperatureParameters
} from "./TemperatureParameters";
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "./ModuleParameters";

export class PVArray {
  name: string;
  make_model: string;
  module_parameters: PVSystModuleParameters | PVWattsModuleParameters;
  temperature_model_parameters:
    | Array<number>
    | PVSystTemperatureParameters
    | PVWattsTemperatureParameters;
  tracking: FixedTrackingParameters | SingleAxisTrackingParameters;
  // PVSyst parameters
  modules_per_string: number;
  strings: number;
  losses_parameters: object; // eslint-disable-line

  constructor({
    name = "New Array",
    make_model = "ABC 123",
    module_parameters = new PVSystModuleParameters({}),
    temperature_model_parameters = new PVSystTemperatureParameters({}),
    tracking = new FixedTrackingParameters({}),
    modules_per_string = 0,
    strings = 0,
    losses_parameters = {}
  }: Partial<PVArray>) {
    this.name = name;
    this.make_model = make_model;
    this.modules_per_string = modules_per_string;
    this.strings = strings;
    this.losses_parameters = losses_parameters;

    if (PVWattsModuleParameters.isInstance(module_parameters)) {
      this.module_parameters = new PVWattsModuleParameters(module_parameters);
    } else if (PVSystModuleParameters.isInstance(module_parameters)) {
      this.module_parameters = new PVSystModuleParameters(module_parameters);
    } else {
      // TODO: raise error/provide warning
      this.module_parameters = new PVWattsModuleParameters({});
    }

    if (FixedTrackingParameters.isInstance(tracking)) {
      this.tracking = new FixedTrackingParameters(tracking);
    } else {
      this.tracking = new SingleAxisTrackingParameters(tracking);
    }

    if (PVSystTemperatureParameters.isInstance(temperature_model_parameters)) {
      this.temperature_model_parameters = new PVSystTemperatureParameters(
        temperature_model_parameters
      );
    } else if (
      PVWattsTemperatureParameters.isInstance(temperature_model_parameters)
    ) {
      this.temperature_model_parameters = new PVWattsTemperatureParameters(
        temperature_model_parameters
      );
    } else {
      this.temperature_model_parameters = temperature_model_parameters;
    }
  }
  static isInstance(obj: any): obj is PVArray {
    const maybe = obj as PVArray;
    return maybe.name != undefined;
    maybe.make_model != undefined;
    maybe.module_parameters != undefined;
    maybe.temperature_model_parameters != undefined;
    maybe.tracking != undefined;
    maybe.modules_per_string != undefined;
    maybe.strings != undefined, maybe.losses_parameters != undefined;
  }
}
