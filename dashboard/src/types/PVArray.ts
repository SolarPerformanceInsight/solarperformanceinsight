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
  makeModel: string;
  moduleParameters: PVSystModuleParameters | PVWattsModuleParameters;
  temperatureModelParameters: Array<number> | PvsystTemperatureParameters;
  tracking: FixedTrackingParameters | SingleAxisTrackingParameters;
  // PVSyst parameters
  modulesPerString: number;
  strings: number;
  lossesParameters: any;

  constructor({
    name = "New Array",
    makeModel = "ABC 123",
    moduleParameters = new PVSystModuleParameters(),
    temperatureModelParameters = [],
    tracking = new FixedTrackingParameters(),
    modulesPerString = 0,
    strings = 0,
    lossesParameters = {}
  } = {}) {
    this.name = name;
    this.makeModel = makeModel;
    this.modulesPerString = modulesPerString;
    this.strings = strings;
    this.lossesParameters = lossesParameters;

    if (moduleParameters instanceof PVWattsModuleParameters) {
      this.moduleParameters = new PVWattsModuleParameters(moduleParameters);
    } else {
      this.moduleParameters = new PVSystModuleParameters(moduleParameters);
    }

    if (tracking instanceof FixedTrackingParameters) {
      this.tracking = new FixedTrackingParameters(tracking);
    } else {
      this.tracking = new SingleAxisTrackingParameters(tracking);
    }

    if (temperatureModelParameters instanceof PvsystTemperatureParameters) {
      this.temperatureModelParameters = new PvsystTemperatureParameters(
        temperatureModelParameters
      );
    } else {
      this.temperatureModelParameters = temperatureModelParameters;
    }
  }
}
