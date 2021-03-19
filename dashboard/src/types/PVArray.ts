import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "./Tracking";
import {
  PVSystTemperatureParameters,
  SAPMTemperatureParameters,
  NOCTSAMTemperatureParameters
} from "./TemperatureParameters";
import {
  PVSystModuleParameters,
  PVWattsModuleParameters,
  CECModuleParameters
} from "./ModuleParameters";

export class PVArray {
  name: string;
  make_model: string;
  module_parameters:
    | PVSystModuleParameters
    | PVWattsModuleParameters
    | CECModuleParameters;
  temperature_model_parameters:
    | Array<number>
    | PVSystTemperatureParameters
    | SAPMTemperatureParameters
    | NOCTSAMTemperatureParameters;
  tracking: FixedTrackingParameters | SingleAxisTrackingParameters;
  // PVSyst parameters
  albedo: number;
  modules_per_string: number;
  strings: number;

  constructor({
    name = "",
    make_model = "",
    module_parameters = new PVSystModuleParameters({}),
    temperature_model_parameters = new PVSystTemperatureParameters({}),
    tracking = new FixedTrackingParameters({}),
    albedo = 0,
    modules_per_string = 1,
    strings = 1
  }: Partial<PVArray>) {
    this.name = name;
    this.make_model = make_model;
    this.albedo = albedo;
    this.modules_per_string = modules_per_string;
    this.strings = strings;

    if (PVWattsModuleParameters.isInstance(module_parameters)) {
      this.module_parameters = new PVWattsModuleParameters(module_parameters);
    } else if (CECModuleParameters.isInstance(module_parameters)) {
      this.module_parameters = new CECModuleParameters(module_parameters);
    } else {
      this.module_parameters = new PVSystModuleParameters(module_parameters);
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
      SAPMTemperatureParameters.isInstance(temperature_model_parameters)
    ) {
      this.temperature_model_parameters = new SAPMTemperatureParameters(
        temperature_model_parameters
      );
    } else {
      this.temperature_model_parameters = temperature_model_parameters;
    }
  }
  static isInstance(obj: any): obj is PVArray {
    const maybe = obj as PVArray;
    return (
      maybe.name != undefined &&
      maybe.make_model != undefined &&
      maybe.module_parameters != undefined &&
      maybe.temperature_model_parameters != undefined &&
      maybe.tracking != undefined &&
      maybe.albedo != undefined &&
      maybe.modules_per_string != undefined &&
      maybe.strings != undefined
    );
  }
}
