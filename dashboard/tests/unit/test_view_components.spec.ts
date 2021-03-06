import Vue from "vue";
import Vuex from "vuex";
import VueRouter from "vue-router";
import flushPromises from "flush-promises";

import { createLocalVue, shallowMount } from "@vue/test-utils";

import SystemSpec from "@/views/SystemSpec.vue";
import Systems from "@/views/Systems.vue";

import { $auth } from "./mockauth";
import { storeObject } from "./mockstore";

import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import {
  PVWattsInverterParameters,
  SandiaInverterParameters
} from "@/types/InverterParameters.ts";
import { PVArray } from "@/types/PVArray";
import {
  PVSystModuleParameters,
  CECModuleParameters
} from "@/types/ModuleParameters";

import { modelSpecs } from "@/types/ModelSpecification";

import { $validator } from "./mockvalidator";

const router = new VueRouter({ mode: "history", base: process.env.BASE_URL });
const localVue = createLocalVue();
localVue.use(Vuex);

const store = new Vuex.Store(storeObject);

const mocks = {
  $auth,
  $validator
};

localVue.use(VueRouter);

const system = new System({ name: "Test" });

let fetchMock: any = {};

global.fetch = jest.fn(() => Promise.resolve(fetchMock));

beforeAll(() => {
  $validator.init();
});

beforeEach(() => {
  fetchMock = {
    // reset the mocked response so each test can alter as needed.
    ok: true,
    json: jest.fn().mockResolvedValue({ definition: system }),
    status: 200
  };
  // @ts-expect-error
  if (router.history.current.path != "/") {
    router.push("/"); // push root to avoid redundancy warnings
  }
  jest.clearAllMocks();
});

import ModelField from "@/components/ModelField.vue";
import InvertersView from "@/components/model/Inverters.vue";
Vue.component("model-field", ModelField);
Vue.component("inverters-view", InvertersView);

describe("Test SystemSpec view", () => {
  it("Test load system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      router,
      store,
      propsData: {
        systemId: "banana"
      },
      mocks
    });
    await flushPromises();
    expect(wrapper.vm.$data.system).toEqual(system);
  });
  it("Test new system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      mocks,
      router,
      store
    });
    await flushPromises();
    expect(wrapper.vm.$data.system).toEqual(new System({}));
  });
  it("Test load system failure", async () => {
    fetchMock.ok = false;
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      propsData: {
        systemId: "banana"
      },
      router,
      mocks,
      store
    });
    await flushPromises();
    expect(wrapper.vm.$data.errorState).toBe(true);
  });
  it("Test save system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      router,
      mocks
    });
    jest.spyOn(router, "push");
    // @ts-expect-error
    wrapper.vm.updateSpecValidity(true);
    await flushPromises();

    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(wrapper.vm.$data.apiErrors).toEqual({});
    expect(router.push).toHaveBeenCalledWith("/systems");
    expect(fetch).toHaveBeenLastCalledWith("/api/systems/", expect.anything());
  });
  it("Test save existing system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      propsData: {
        systemId: "banana"
      },
      router,
      mocks
    });
    await flushPromises();
    // @ts-expect-error
    wrapper.vm.updateSpecValidity(true);
    await flushPromises();
    expect(wrapper.vm.$data.specValid).toBe(true);
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(wrapper.vm.$data.apiErrors).toEqual({});
    expect(wrapper.vm.$data.system).toEqual(system);
    expect(fetch).toHaveBeenLastCalledWith(
      "/api/systems/banana",
      expect.anything()
    );
  });
  it("Test save system failure", async () => {
    fetchMock.ok = false;
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      mocks,
      router
    });
    // @ts-expect-error
    wrapper.vm.updateSpecValidity(true);
    jest.spyOn(router, "push");
    await flushPromises();
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(router.push).not.toHaveBeenCalled();
    expect(wrapper.vm.$data.apiErrors).toEqual(await fetchMock.json());
  });
  it("Test save system failure no json", async () => {
    fetchMock.ok = false;
    fetchMock.json.mockImplementation(() => {
      throw new Error("broken");
    });
    fetchMock.status = 500;
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      mocks,
      router
    });
    // @ts-expect-error
    wrapper.vm.updateSpecValidity(true);
    await flushPromises();
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(wrapper.vm.$data.apiErrors).toEqual({
      error: "API responded with status code: 500"
    });
    expect(router.push).not.toHaveBeenCalled();
  });
  it("Test infer pvwatts", async () => {
    const jsonResponse = {
      definition: new System({
        inverters: [
          new Inverter({
            inverter_parameters: new PVWattsInverterParameters({})
          })
        ]
      })
    };
    fetchMock.json = jest.fn().mockResolvedValue(jsonResponse);
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      propsData: {
        systemId: "someid"
      },
      mocks,
      router
    });
    await flushPromises();
    expect(wrapper.vm.$data.model).toBe("pvwatts");
    // @ts-expect-error
    expect(wrapper.vm.modelSpec).toEqual(modelSpecs["pvwatts"]);
  });
  it("Test infer pvsyst", async () => {
    fetchMock.json = jest.fn().mockResolvedValue({
      definition: new System({
        inverters: [
          new Inverter({
            inverter_parameters: new SandiaInverterParameters({}),
            arrays: [
              new PVArray({
                module_parameters: new PVSystModuleParameters({})
              })
            ]
          })
        ]
      })
    });
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      propsData: {
        systemId: "someid"
      },
      mocks,
      router
    });
    await flushPromises();
    expect(wrapper.vm.$data.model).toBe("pvsyst");
    // @ts-expect-error
    expect(wrapper.vm.modelSpec).toEqual(modelSpecs["pvsyst"]);
  });
  it("Test upload handling", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      mocks,
      router
    });
    await flushPromises();
    const theSystem = new System({
      inverters: [
        new Inverter({
          inverter_parameters: new SandiaInverterParameters({})
        })
      ]
    });
    const theString = JSON.stringify(theSystem);
    // @ts-expect-error
    wrapper.vm.uploadSuccess(theString);
    expect(wrapper.vm.$data.system).toEqual(theSystem);
  });
  it("Test infer sam", async () => {
    fetchMock.json = jest.fn().mockResolvedValue({
      definition: new System({
        inverters: [
          new Inverter({
            inverter_parameters: new SandiaInverterParameters({}),
            arrays: [
              new PVArray({
                module_parameters: new CECModuleParameters({})
              })
            ]
          })
        ]
      })
    });
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      propsData: {
        systemId: "someid"
      },
      mocks,
      router
    });
    await flushPromises();
    expect(wrapper.vm.$data.model).toBe("sam");
    // @ts-expect-error
    expect(wrapper.vm.modelSpec).toEqual(modelSpecs["sam"]);
  });
  it("Test upload handling", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      store,
      mocks,
      router
    });
    await flushPromises();
    const theSystem = new System({
      inverters: [
        new Inverter({
          inverter_parameters: new SandiaInverterParameters({})
        })
      ]
    });
    const theString = JSON.stringify(theSystem);
    // @ts-expect-error
    wrapper.vm.uploadSuccess(theString);
    expect(wrapper.vm.$data.system).toEqual(theSystem);
  });
});
describe("Test Systems view", () => {
  it("test delete a site", async () => {
    const wrapper = shallowMount(Systems, {
      localVue,
      store,
      mocks,
      router
    });
    await flushPromises();
    expect(wrapper.find(".system-name").text()).toBe("Super System");
    expect(wrapper.find("modal-block").exists()).toBe(false);
    const deleteLink = wrapper.find("a.delete-button");
    deleteLink.trigger("click");
    await flushPromises();
    const deleteModal = wrapper.find(".modal-block");
    expect(deleteModal.exists()).toBe(true);
    deleteModal.find(".confirm-deletion").trigger("click");
    await flushPromises();
    expect(fetch).toHaveBeenCalledWith(
      "/api/systems/someuuid",
      expect.anything()
    );
    expect(wrapper.find(".modal-block").exists()).toBe(false);
  });
  it("test delete a site", async () => {
    const wrapper = shallowMount(Systems, {
      localVue,
      store,
      mocks,
      router
    });
    await flushPromises();
    expect(wrapper.find(".system-name").text()).toBe("Super System");
    expect(wrapper.find("modal-block").exists()).toBe(false);
    const deleteLink = wrapper.find("a.delete-button");
    deleteLink.trigger("click");
    await flushPromises();
    const deleteModal = wrapper.find(".modal-block");
    expect(deleteModal.exists()).toBe(true);
    deleteModal.find(".cancel-deletion").trigger("click");
    await flushPromises();
    expect(fetch).not.toHaveBeenCalled();
    expect(wrapper.find(".modal-block").exists()).toBe(false);
  });
});
