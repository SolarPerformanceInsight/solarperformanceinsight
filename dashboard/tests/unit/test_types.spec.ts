import { shallowMount } from "@vue/test-utils";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import { PVSystModuleParameters } from "@/types/ModuleParameters";
import { FixedTrackingParameters } from "@/types/Tracking";
import { PVSystTemperatureParameters } from "@/types/TemperatureParameters";

test("Instantiate base system", () => {
  const system = new System();
  expect(system instanceof System).toBeTruthy();
  const inverters = system.inverters;
  expect(inverters instanceof Array).toBeTruthy();
  for (let i = 0; i < inverters.length; i++) {
    const inverter = inverters[i];
    expect(inverter instanceof Inverter).toBeTruthy();
    expect(typeof inverter.make_model).toBe("string");
    const arrays = inverter.arrays;
    expect(arrays instanceof Array).toBeTruthy();
    for (let i = 0; i < arrays.length; i++) {
      const array = arrays[i];
      expect(array instanceof PVArray).toBeTruthy();
      expect(
        array.module_parameters instanceof PVSystModuleParameters
      ).toBeTruthy();
      expect(array.tracking instanceof FixedTrackingParameters).toBeTruthy();
      expect(array.temperature_model_parameters instanceof Array).toBeTruthy();
    }
  }
});
