import Vue from "vue";

import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import ArrayView from "@/components/model/Array.vue";
import ArraysView from "@/components/model/Arrays.vue";
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
    return { parameters: { name: "Name" } };
  }
}).vm;

const mocks = {};

beforeEach(() => {
  jest.clearAllMocks();
});
function expectAllModelFields(
  wrapper: Wrapper<any>,
  parameters: Record<string, any>
) {
  /* Tests that all parameter properties of type string, number or boolean
   * exist as <model-field> components in the wrapper.
   */

  const modelFieldKeys = Object.keys(parameters).filter(k => {
    return ["string", "number", "boolean"].includes(typeof parameters[k]);
  });
  const fields = wrapper.findAllComponents(ModelField);
  expect(fields).toHaveLength(modelFieldKeys.length);
  const fieldProps = fields.wrappers.map(function(w: any) {
    return w.props("fieldName");
  });
  for (const field of modelFieldKeys) {
    expect(fieldProps.includes(field)).toBe(true);
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
    const wrapper = shallowMount(TemperatureParametersView, {
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
    const wrapper = shallowMount(TemperatureParametersView, {
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
    const wrapper = shallowMount(LossParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("pvwatts", () => {
    const propsData = {
      parameters: null,
      model: "pvsyst"
    };
    const wrapper = shallowMount(LossParametersView, {
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
    const wrapper = shallowMount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
  it("singleAxis", () => {
    const propsData = {
      parameters: new SingleAxisTrackingParameters({}),
      tracking: "singleAxis"
    };
    const wrapper = shallowMount(TrackingParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
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
    const wrapper = shallowMount(ModuleParametersView, {
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
    const wrapper = shallowMount(ModuleParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
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
    expectAllModelFields(wrapper, propsData.parameters);
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
    expectAllModelFields(wrapper, propsData.parameters);
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
    expectAllModelFields(wrapper, propsData.parameters);
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
    expectAllModelFields(wrapper, propsData.parameters);
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
    const wrapper = shallowMount(InverterParametersView, {
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
    const wrapper = shallowMount(InverterParametersView, {
      localVue,
      propsData,
      mocks
    });
    expectAllModelFields(wrapper, propsData.parameters);
  });
});
