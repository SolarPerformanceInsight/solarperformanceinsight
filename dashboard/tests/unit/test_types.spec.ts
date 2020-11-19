import { shallowMount } from "@vue/test-utils";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import { PVSystModuleParameters } from "@/types/ModuleParameters";
import { FixedTrackingParameters } from "@/types/Tracking";
import { PVSystTemperatureParameters } from "@/types/TemperatureParameters";

test("Instantiate base system", () => {
  const system = new System({});
  expect(system instanceof System).toBeTruthy();
  const inverters = system.inverters;
  expect(inverters instanceof Array).toBeTruthy();
  expect(inverters.length).toBe(0);
});


const pvsyst_test_system = {
  name: "Test System",
  latitude: 0,
  longitude: 0,
  elevation: 0,
  albedo: 0,
  inverters: [
    {
      name: "New Inverter",
      make_model: "ABC 520",
      inverter_parameters: {
        Paco: 0,
        Pdco: 0,
        Vdco: 0,
        Pso: 0,
        C0: 0,
        C1: 0,
        C2: 0,
        C3: 0,
        Pnt: 0
      },
      losses_parameters: {},
      arrays: [
        {
          name: "New Array",
          make_model: "ABC 123",
          modules_per_string: 0,
          strings: 0,
          losses_parameters: {},
          module_parameters: {
            gamma_ref: 0,
            mu_gamma: 0,
            I_L_ref: 0,
            I_o_ref: 0,
            R_sh_ref: 0,
            R_sh_0: 0,
            R_s: 0,
            alpha_sc: 0,
            EgRef: 0,
            cells_in_series: 0
          },
          tracking: {
            tilt: 0,
            azimuth: 0
          },
          temperature_model_parameters: {
            uC: 29,
            uV: 0
          }
        }
      ]
    }
  ]
};
test("PVArray Instance", () => {
  const array: PVArray = new PVArray(
      pvsyst_test_system['inverters'][0]['arrays'][0]);
});
test("Inverter Instance", () => {
  const inverter: Inverter = new Inverter(pvsyst_test_system['inverters'][0]);
});

test("Instantiate system from object", () => {
  const system: System = new System(pvsyst_test_system);
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
      expect(
        array.temperature_model_parameters instanceof
          PVSystTemperatureParameters
      ).toBeTruthy();
    }
  }
});
