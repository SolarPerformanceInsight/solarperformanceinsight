import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "./Tracking";
import { ModuleParameters } from "./Module";

export class PVArray {
  name: string;
  makeModel: string;
  moduleParameters: ModuleParamters;
  temperatureModelParameters: Array<number>;
  tracking: FixedTrackingParameters | SingleAxisTrackingParameters;
  // PVSyst parameters
  modulesPerString: number;
  strings: number;
  lossesParameters: any;

  constructor({
    name = "New Array",
    makeModel = "ABC 123",
    moduleParameters = {},
    temperatureModuleParameters = [],
    tracking = new FixedTrackingParameters(),
    modulesPerString = 0,
    strings = 0,
    lossesParameters = {}
  } = {}) {
    this.name = name;
    this.makeModel = makeModel;
    this.moduleParameters = moduleParameters;
    this.temperatureModuleParameters = temperatureModuleParameters;
    this.tracking = tracking;
    this.modulesPerString = modulesPerString;
    this.strings = strings;
    this.lossesParameters = lossesParameters;
  }
}
