import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import { APIValidator } from "@/types/validation/Validator";
import APISpec from "./openapi.json";

import ArrayView from "@/components/model/Array.vue";
import ArraysView from "@/components/model/Arrays.vue";
import DBBrowser from "@/components/Browser.vue";
import HelpPopup from "@/components/Help.vue";
import Home from "@/views/Home.vue";
import InverterView from "@/components/model/Inverter.vue";
import InvertersView from "@/components/model/Inverters.vue";
import InverterParametersView from "@/components/model/InverterParameters.vue";
import LossParametersView from "@/components/model/LossParameters.vue";
import ModelField from "@/components/ModelField.vue";
import ModuleParametersView from "@/components/model/ModuleParameters.vue";
import TemperatureParametersView from "@/components/model/TemperatureParameters.vue";
import TrackingParametersView from "@/components/model/TrackingParameters.vue";
import FileUpload from "@/components/FileUpload.vue";
import SystemView from "@/components/model/System.vue";

const localVue = createLocalVue();

Vue.component("array-view", ArrayView);
Vue.component("arrays-view", ArraysView);
Vue.component("db-browser", DBBrowser);
Vue.component("help", HelpPopup);
Vue.component("home", Home);
Vue.component("inverter-view", InverterView);
Vue.component("inverters-view", InvertersView);
Vue.component("inverter-parameters", InverterParametersView);
Vue.component("loss-parameters", LossParametersView);
Vue.component("model-field", ModelField);
Vue.component("module-parameters", ModuleParametersView);
Vue.component("tracking-parameters", TrackingParametersView);
Vue.component("temperature-parameters", TemperatureParametersView);
Vue.component("system-view", SystemView);
Vue.component("file-upload", FileUpload);

// $parent not accessible inside tests, add a simple patch for ensuring name
// stubs work
const grandParentComponent: Vue = mount({
  template: "<div />",
  data() {
    return { parameters: { name: "Name" } };
  }
}).vm;

const parentComponent: Vue = mount({
  created() {
    this.parent = grandParentComponent;
  },
  template: "<div />",
  data() {
    return {
      parameters: { name: "Name" }
    };
  }
}).vm;

const $validator = new APIValidator();
$validator.getAPISpec = jest.fn().mockResolvedValue(APISpec);

const mocks = {
  $validator
};

let fetchMock: any = {};
global.fetch = jest.fn(() => Promise.resolve(fetchMock));

beforeAll(() => {
  $validator.init();
});

beforeEach(() => {
  jest.clearAllMocks();
});

function expectAllModelFields(
  wrapper: Wrapper<any>,
  parameters: Record<string, any>
) {
  /* Tests that all parameter properties of type string, number or boolean
   * exist as <model-field> components in the wrapper and that values are
   * set to values of the passed in parameters.
   */
  const modelFieldKeys = Object.keys(parameters).filter(k => {
    return ["string", "number", "boolean"].includes(typeof parameters[k]);
  });

  const fields = wrapper.findAllComponents(ModelField);
  expect(fields).toHaveLength(modelFieldKeys.length);
  for (const fw of fields.wrappers) {
    const fn = fw.props("fieldName");
    let inp: any;
    if (typeof parameters[fn] == "boolean") {
      inp = fw.find("input[type=radio]:checked");
    } else {
      inp = fw.find("input");
    }
    expect(inp.element.value).toEqual(parameters[fn].toString());
  }
}

function expectAllModelFieldsShallow(
  wrapper: Wrapper<any>,
  parameters: Record<string, any>
) {
  /* Tests that all parameter properties of type string, number or boolean
   * exist as <model-field> components. Used to test shallow-mounted components
   * that would normally contain model fields of other nested components.
   */
  const modelFieldKeys = Object.keys(parameters).filter(k => {
    return ["string", "number", "boolean"].includes(typeof parameters[k]);
  });

  const fields = wrapper.findAllComponents(ModelField);
  expect(fields).toHaveLength(modelFieldKeys.length);
  for (const fw of fields.wrappers) {
    const fn = fw.props("fieldName");
    expect(fn in parameters).toBe(true);
  }
}

function fillEmptyString(spec: Record<string, any>) {
  for (const k in spec) {
    spec[k] = "";
  }
}
async function expectAllErrors(wrapper: Wrapper<any>, keys: Array<string>) {
  wrapper.vm.validate(wrapper.props("parameters"));
  await flushPromises();
  for (const k of keys) {
    if (!["name", "make_model"].includes(k)) {
      expect(k in wrapper.vm.errors).toBe(true);
    }
  }
}
/*
 * Temperature Parameters
 */
import {
  PVSystTemperatureParameters,
  SAPMTemperatureParameters
} from "@/types/TemperatureParameters";
describe("Tests temperature parameters", () => {
  it("pvsyst", () => {
    const propsData = {
      parameters: new PVSystTemperatureParameters({}),
      model: "pvsyst"
    };
    const wrapper = mount(TemperatureParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvwatts", () => {
    const propsData = {
      parameters: new SAPMTemperatureParameters({}),
      model: "pvwatts"
    };
    const wrapper = mount(TemperatureParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
});

/*
 * Loss Parameters
 */
import { PVWattsLosses } from "@/types/Losses";
describe("Tests Loss Parameters", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new PVWattsLosses({}),
      model: "pvwatts"
    };
    const wrapper = mount(LossParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvwatts errors", async () => {
    const propsData = {
      parameters: new PVWattsLosses({}),
      model: "pvwatts"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(LossParametersView, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("PVWattsLosses");
    await expectAllErrors(wrapper, Object.keys(new PVWattsLosses({})));
  });

  it("pvsyst", () => {
    const propsData = {
      parameters: null,
      model: "pvsyst"
    };
    const wrapper = mount(LossParametersView, {
      localVue,
      propsData,
      mocks
    });
    const fields = wrapper.findAllComponents(ModelField);
    expect(fields).toHaveLength(0);
  });
});

/*
 * Tracking Parameters
 */
import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";
describe("Test tracking parameters", () => {
  it("fixed", () => {
    const propsData = {
      parameters: new FixedTrackingParameters({}),
      tracking: "fixed"
    };
    const wrapper = mount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("fixed errors", async () => {
    const propsData = {
      parameters: new FixedTrackingParameters({}),
      tracking: "fixed"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("FixedTracking");
    await expectAllErrors(
      wrapper,
      Object.keys(new FixedTrackingParameters({}))
    );
  });
  it("singleAxis", () => {
    const propsData = {
      parameters: new SingleAxisTrackingParameters({}),
      tracking: "singleAxis"
    };
    const wrapper = mount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("singleAxis errors", async () => {
    const propsData = {
      parameters: new SingleAxisTrackingParameters({}),
      tracking: "singleAxis"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("SingleAxisTracking");
    await expectAllErrors(
      wrapper,
      Object.keys(new SingleAxisTrackingParameters({}))
    );
  });
});

/*
 * Module Parameters
 */
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";
describe("Test module parameters", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new PVWattsModuleParameters({}),
      model: "pvwatts"
    };
    const wrapper = mount(ModuleParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvsyst", () => {
    const propsData = {
      parameters: new PVSystModuleParameters({}),
      model: "pvsyst"
    };
    const wrapper = mount(ModuleParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvsyst component name and validation", async () => {
    const propsData = {
      parameters: new PVSystModuleParameters({}),
      model: "pvsyst"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(ModuleParametersView, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("PVsystModuleParameters");
    await expectAllErrors(wrapper, Object.keys(new PVSystModuleParameters({})));
  });
  it("pvwatts component name and validation", async () => {
    const propsData = {
      parameters: { pdc0: "", gamma_pdc: "" },
      model: "pwatts"
    };
    const wrapper = mount(ModuleParametersView, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("PVWattsModuleParameters");
    await expectAllErrors(
      wrapper,
      Object.keys(new PVWattsModuleParameters({}))
    );
  });
});
/*
 * PV Array
 */

import { PVArray } from "@/types/PVArray";
describe("Test array", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expectAllModelFieldsShallow(wrapper, propsData.parameters);
    const mp = wrapper.findComponent(ModuleParametersView);
    expect(mp.exists()).toBe(true);
    expect(mp.props("model")).toBe("pvwatts");
    expect(mp.props("parameters")).toEqual(
      propsData.parameters.module_parameters
    );
    const tp = wrapper.findComponent(TemperatureParametersView);
    expect(tp.exists()).toBe(true);
    expect(tp.props("model")).toBe("pvwatts");
    expect(tp.props("parameters")).toEqual(
      propsData.parameters.temperature_model_parameters
    );
    const trp = wrapper.findComponent(TrackingParametersView);
    expect(trp.exists()).toBe(true);
    expect(trp.props("tracking")).toBe("fixed");
    expect(trp.props("parameters")).toEqual(propsData.parameters.tracking);
  });
  it("pvsyst", () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVSystModuleParameters({}),
        temperature_model_parameters: new PVSystTemperatureParameters({}),
        tracking: new SingleAxisTrackingParameters({})
      }),
      model: "pvsyst"
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expectAllModelFieldsShallow(wrapper, propsData.parameters);
    const mp = wrapper.findComponent(ModuleParametersView);
    expect(mp.exists()).toBe(true);
    expect(mp.props("model")).toBe("pvsyst");
    expect(mp.props("parameters")).toEqual(
      propsData.parameters.module_parameters
    );
    const tp = wrapper.findComponent(TemperatureParametersView);
    expect(tp.exists()).toBe(true);
    expect(tp.props("model")).toBe("pvsyst");
    expect(tp.props("parameters")).toEqual(
      propsData.parameters.temperature_model_parameters
    );
    const trp = wrapper.findComponent(TrackingParametersView);
    expect(trp.exists()).toBe(true);
    expect(trp.props("tracking")).toBe("singleAxis");
    expect(trp.props("parameters")).toEqual(propsData.parameters.tracking);
  });
  it("test tracking change", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expect(wrapper.vm.$data.tracking).toBe("fixed");
    const trackingView = wrapper.findComponent(TrackingParametersView);
    expect(
      FixedTrackingParameters.isInstance(trackingView.props("parameters"))
    ).toBe(true);

    // Test that button click alters class in tracking view
    const singleAxisButton = wrapper.find("input[value=singleAxis]");
    singleAxisButton.trigger("click");
    await Vue.nextTick();
    expect(wrapper.vm.$data.tracking).toBe("singleAxis");
    expect(
      SingleAxisTrackingParameters.isInstance(
        wrapper.props("parameters").tracking
      )
    ).toBe(true);

    expect(
      SingleAxisTrackingParameters.isInstance(trackingView.props("parameters"))
    ).toBe(true);
    const fixedButton = wrapper.find("input[value=fixed");
    fixedButton.trigger("click");
    await Vue.nextTick();
    expect(wrapper.vm.$data.tracking).toBe("fixed");
    expect(
      FixedTrackingParameters.isInstance(wrapper.props("parameters").tracking)
    ).toBe(true);
  });
  it("test ensureTracking", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expect(wrapper.vm.$data.tracking).toBe("fixed");
    propsData.parameters.tracking = new SingleAxisTrackingParameters({});
    // @ts-expect-error
    wrapper.vm.ensureTracking();
    expect(wrapper.vm.$data.tracking).toBe("singleAxis");
  });
  it("test array removal", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    expect(wrapper.emitted("array-removed")).toBeFalsy();
    const remove = wrapper.find("button.remove-array");
    remove.trigger("click");
    await Vue.nextTick();
    // @ts-expect-error
    expect(wrapper.emitted("array-removed")[0]).toEqual([0]);
  });
  it("test array duplication", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    expect(wrapper.emitted("array-added")).toBeFalsy();
    const duplicate = wrapper.find("button.duplicate-array");
    duplicate.trigger("click");
    await Vue.nextTick();
    // @ts-expect-error
    expect(wrapper.emitted("array-added")[0]).toEqual([propsData.parameters]);
  });
  it("test errors", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };
    fillEmptyString(propsData.parameters);
    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.apiComponentName).toBe("PVArray");
    await expectAllErrors(wrapper, Object.keys(new PVArray({})));
  });
  it("test change model", async () => {
    const propsData = {
      parameters: new PVArray({
        module_parameters: new PVWattsModuleParameters({}),
        temperature_model_parameters: new SAPMTemperatureParameters({}),
        tracking: new FixedTrackingParameters({})
      }),
      model: "pvwatts",
      index: 0
    };

    // @ts-expect-error
    const wrapper = shallowMount(ArrayView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    // @ts-expect-error
    wrapper.vm.changeModel("pvsyst");

    expect(
      PVSystModuleParameters.isInstance(propsData.parameters.module_parameters)
    ).toBe(true);
    expect(
      PVSystTemperatureParameters.isInstance(
        propsData.parameters.temperature_model_parameters
      )
    ).toBe(true);

    // @ts-expect-error
    wrapper.vm.changeModel("pvwatts");
    expect(
      PVWattsModuleParameters.isInstance(propsData.parameters.module_parameters)
    ).toBe(true);
    expect(
      SAPMTemperatureParameters.isInstance(
        propsData.parameters.temperature_model_parameters
      )
    ).toBe(true);
  });
});

/*
 * PV Arrays
 */

describe("PV Arrays", () => {
  it("Test adding arrays", () => {
    const propsData = {
      pvarrays: [] as Array<PVArray>,
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArraysView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    expect(propsData.pvarrays).toHaveLength(0);
    wrapper.find("button").trigger("click");
    expect(propsData.pvarrays).toHaveLength(1);
    const defaultAlbedo = propsData.pvarrays[0].albedo;
    // change albedo and make sure new array have this value
    const initAlbedo = 1.2;
    propsData.pvarrays[0].albedo = initAlbedo;
    wrapper.find("button").trigger("click");
    expect(propsData.pvarrays).toHaveLength(2);
    expect(propsData.pvarrays[1].albedo).toBe(initAlbedo);
    wrapper.find("button").trigger("click");
    expect(propsData.pvarrays).toHaveLength(3);
    expect(propsData.pvarrays[2].albedo).toBe(initAlbedo);
    // if one array has different albedo, others added have default
    propsData.pvarrays[1].albedo = 99.8;
    wrapper.find("button").trigger("click");
    expect(propsData.pvarrays).toHaveLength(4);
    expect(propsData.pvarrays[3].albedo).toBe(defaultAlbedo);
  });
  it("Test adding arrays", () => {
    const propsData = {
      pvarrays: [] as Array<PVArray>,
      model: "pvsyst",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArraysView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    wrapper.find("button").trigger("click");
    expect(propsData.pvarrays).toHaveLength(1);
    expect(
      PVSystModuleParameters.isInstance(propsData.pvarrays[0].module_parameters)
    ).toBe(true);
    expect(
      PVSystTemperatureParameters.isInstance(
        propsData.pvarrays[0].temperature_model_parameters
      )
    ).toBe(true);
  });
  it("Test event handling", async () => {
    const propsData = {
      pvarrays: [new PVArray({})],
      model: "pvsyst",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(ArraysView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    const arr = wrapper.findComponent(ArrayView);
    arr.vm.$emit("array-added", propsData.pvarrays[0]);
    expect(propsData.pvarrays).toHaveLength(2);
    expect(propsData.pvarrays[0]).toEqual(propsData.pvarrays[1]);
    propsData.pvarrays[1].name = "array 2";
    arr.vm.$emit("array-removed", 0);
    expect(propsData.pvarrays).toHaveLength(1);
    expect(propsData.pvarrays[0].name).toBe("array 2");
  });
});

/*
 * Inverter
 */

import { Inverter } from "@/types/Inverter";
import {
  PVWattsInverterParameters,
  SandiaInverterParameters
} from "@/types/InverterParameters";
describe("Test Inverter", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new PVWattsInverterParameters({}),
        losses: new PVWattsLosses({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expectAllModelFieldsShallow(wrapper, propsData.parameters);
    const ip = wrapper.findComponent(InverterParametersView);
    expect(ip.exists()).toBe(true);
    expect(ip.props("model")).toBe("pvwatts");
    expect(ip.props("parameters")).toEqual(
      propsData.parameters.inverter_parameters
    );
    const lp = wrapper.findComponent(LossParametersView);
    expect(lp.exists()).toBe(true);
    expect(lp.props("model")).toBe("pvwatts");
    expect(lp.props("parameters")).toEqual(propsData.parameters.losses);
    const arrays = wrapper.findComponent(ArraysView);
    expect(arrays.exists()).toBe(true);
    expect(arrays.props("model")).toBe("pvwatts");
    expect(arrays.props("pvarrays")).toEqual(propsData.parameters.arrays);
  });
  it("pvsyst", () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new SandiaInverterParameters({}),
        losses: null
      }),
      model: "pvsyst",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expectAllModelFieldsShallow(wrapper, propsData.parameters);
    const ip = wrapper.findComponent(InverterParametersView);
    expect(ip.exists()).toBe(true);
    expect(ip.props("model")).toBe("pvsyst");
    expect(ip.props("parameters")).toEqual(
      propsData.parameters.inverter_parameters
    );
    const lp = wrapper.findComponent(LossParametersView);
    expect(lp.exists()).toBe(false);

    const arrays = wrapper.findComponent(ArraysView);
    expect(arrays.exists()).toBe(true);
    expect(arrays.props("model")).toBe("pvsyst");
    expect(arrays.props("pvarrays")).toEqual(propsData.parameters.arrays);
  });
  it("test inverter duplication", async () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new PVWattsInverterParameters({}),
        losses: new PVWattsLosses({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    expect(wrapper.emitted("inverter-added")).toBeFalsy();
    const duplicate = wrapper.find("button.duplicate-inverter");
    duplicate.trigger("click");
    await Vue.nextTick();
    // @ts-expect-error
    expect(wrapper.emitted("inverter-added")[0]).toEqual([
      propsData.parameters
    ]);
  });
  it("test inverter removal", async () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new PVWattsInverterParameters({}),
        losses: new PVWattsLosses({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });

    expect(wrapper.emitted("inverter-removed")).toBeFalsy();
    const remove = wrapper.find("button.remove-inverter");
    remove.trigger("click");
    await Vue.nextTick();
    // @ts-expect-error
    expect(wrapper.emitted("inverter-removed")[0]).toEqual([0]);
  });
  it("test modelchange", () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new PVWattsInverterParameters({}),
        losses: new PVWattsLosses({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    // @ts-expect-error
    wrapper.vm.changeModel("pvsyst");
    expect(
      SandiaInverterParameters.isInstance(
        propsData.parameters.inverter_parameters
      )
    ).toBe(true);
    expect(propsData.parameters.losses).toBe(null);
    // @ts-expect-error
    wrapper.vm.changeModel("pvwatts");
    expect(
      PVWattsInverterParameters.isInstance(
        propsData.parameters.inverter_parameters
      )
    ).toBe(true);
    expect(PVWattsLosses.isInstance(propsData.parameters.losses)).toBe(true);
  });
  it("pvwatts", () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new PVWattsInverterParameters({}),
        losses: new PVWattsLosses({})
      }),
      model: "pvwatts",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
  });
  it("test loadInverterParameters", () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new SandiaInverterParameters({}),
        losses: null
      }),
      model: "pvsyst",
      index: 0
    };
    // @ts-expect-error
    const wrapper = shallowMount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    const chosenParameters = {
      name: "ABB__PVI_3_0_OUTD_S_US_Z_A__208V_",
      parameters: {
        Paco: 3000,
        Pdco: 3142.30127,
        Vdco: 310,
        Pso: 18.166279,
        C0: -0.000008039486,
        C1: -0.000011,
        C2: 0.000999,
        C3: -0.00028700000000000004,
        Pnt: 0.1
      }
    };
    // @ts-expect-error
    wrapper.vm.loadInverterParameters(chosenParameters);
    expect(propsData.parameters.make_model).toBe(chosenParameters.name);
    expect(propsData.parameters.inverter_parameters).toStrictEqual(
      new SandiaInverterParameters(chosenParameters.parameters)
    );
  });
});

/*
 * Inverters
 */
describe("Test inverter listing", () => {
  it("test add inverter", async () => {
    const propsData = {
      inverters: [] as Array<Inverter>,
      model: "pvwatts"
    };
    // @ts-expect-error
    const wrapper = shallowMount(InvertersView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expect(propsData.inverters.length).toBe(0);
    const remove = wrapper.find("button");
    remove.trigger("click");
    await Vue.nextTick();
    expect(propsData.inverters.length).toBe(1);
  });
  it("Test event handling", async () => {
    const propsData = {
      inverters: [new Inverter({})],
      model: "pvwatts"
    };
    // @ts-expect-error
    const wrapper = shallowMount(InvertersView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    const arr = wrapper.findComponent(InverterView);
    arr.vm.$emit("inverter-added", propsData.inverters[0]);
    expect(propsData.inverters).toHaveLength(2);
    expect(propsData.inverters[0]).toEqual(propsData.inverters[1]);
    propsData.inverters[1].name = "inverter 2";
    arr.vm.$emit("inverter-removed", 0);
    expect(propsData.inverters).toHaveLength(1);
    expect(propsData.inverters[0].name).toBe("inverter 2");
  });
});

/*
 * Inverter Parameters
 */
describe("Test inverter parameters", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new PVWattsInverterParameters({}),
      model: "pvwatts"
    };
    const wrapper = mount(InverterParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvsyst", () => {
    const propsData = {
      parameters: new SandiaInverterParameters({}),
      model: "pvsyst"
    };
    const wrapper = mount(InverterParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("test pvwatts errors", async () => {
    const propsData = {
      parameters: new PVWattsInverterParameters({}),
      model: "pvwatts"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(InverterParametersView, {
      localVue,
      propsData,
      mocks
    });
    await expectAllErrors(
      wrapper,
      Object.keys(new PVWattsInverterParameters({}))
    );
  });
  it("test pvsyst errors", async () => {
    const propsData = {
      parameters: new SandiaInverterParameters({}),
      model: "pvsyst"
    };
    fillEmptyString(propsData.parameters);
    const wrapper = mount(InverterParametersView, {
      localVue,
      propsData,
      mocks
    });
    await expectAllErrors(
      wrapper,
      Object.keys(new SandiaInverterParameters({}))
    );
  });
  it("test inverter browser display pvsyst", async () => {
    const propsData = {
      parameters: new Inverter({
        inverter_parameters: new SandiaInverterParameters({
          Paco: 10,
          Pdco: 10
        })
      }),
      model: "pvsyst"
    };
    fetchMock = {
      json: jest.fn().mockResolvedValue(["inverter1"])
    };
    // @ts-expect-error
    const wrapper = mount(InverterView, {
      localVue,
      propsData,
      parentComponent,
      mocks
    });
    expect(wrapper.find("div.db-browser").exists()).toBe(false);
    wrapper.find("button.show-browser").trigger("click");

    await flushPromises();

    const browse = wrapper.find("div.db-browser");
    expect(browse.exists()).toBe(true);
    fetchMock.json.mockResolvedValue(new SandiaInverterParameters({}));
    browse.find("option").setSelected();

    await flushPromises();

    browse.find("button.commit").trigger("click");

    await flushPromises();

    expect(wrapper.find("div.db-browser").exists()).toBe(false);
    expect(wrapper.props("parameters").inverter_parameters).toEqual(
      new SandiaInverterParameters({})
    );
    wrapper.find("button.show-browser").trigger("click");

    await flushPromises();

    const browserAgain = wrapper.find("div.db-browser");
    expect(browserAgain.exists()).toBe(true);
    browserAgain.find("button.cancel").trigger("click");

    await flushPromises();

    expect(wrapper.find("div.db-browser").exists()).toBe(false);
  });
});
/*
 * System
 */
import { System } from "@/types/System";
describe("Test System", () => {
  it("pvwatts", () => {
    const propsData = {
      parameters: new System({}),
      model: "pvwatts"
    };
    const wrapper = shallowMount(SystemView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFieldsShallow(wrapper, propsData.parameters);
    const iv = wrapper.findComponent(InvertersView);
    expect(iv.props("model")).toEqual("pvwatts");
    expect(iv.props("inverters")).toEqual(propsData.parameters.inverters);
  });
  it("test system errors", async () => {
    const propsData = {
      parameters: new System({}),
      model: "pvwatts"
    };
    fillEmptyString(propsData.parameters);
    propsData.parameters.name = "*";
    const wrapper = shallowMount(SystemView, {
      localVue,
      propsData,
      mocks
    });
    await expectAllErrors(wrapper, Object.keys(new System({})));
    // @ts-expect-error
    expect("name" in wrapper.vm.errors).toBe(true);
  });
});

/*
 * Model Base
 */
describe("Test model base", () => {
  it("Test validation display", async () => {
    // Using simple class that extends ModelBase and implements methods
    const propsData = {
      parameters: new PVSystTemperatureParameters({}),
      model: "pvsyst"
    };
    const wrapper = mount(TemperatureParametersView, {
      localVue,
      propsData,
      mocks
    });
    await Vue.nextTick();

    // @ts-expect-error
    const defs = wrapper.vm.definitions;
    expect(defs["description"]).toEqual(
      APISpec.components.schemas.PVsystTemperatureParameters.description
    );
    const ucField = wrapper.find("input");

    // @ts-expect-error
    const spy = jest.spyOn(wrapper.vm, "setValidationResult");
    // @ts-expect-error
    const valspy = jest.spyOn(wrapper.vm, "validate");

    // @ts-expect-error
    expect(ucField.element.type).toEqual("number");

    // trigger setValidationResult with validity = false
    ucField.setValue("");
    await Vue.nextTick();

    // Manually trigger watch function, which does not fire in tests
    // @ts-expect-error
    wrapper.vm.validate(wrapper.props("parameters"));

    await flushPromises();

    // @ts-expect-error
    expect(wrapper.vm.setValidationResult).toHaveBeenCalled();

    expect(wrapper.props("parameters").u_c).toBe("");

    // @ts-expect-error
    expect("u_c" in wrapper.vm.errors).toBe(true);
    expect(wrapper.find("span.errors").text()).toEqual("should be number");
  });
});
