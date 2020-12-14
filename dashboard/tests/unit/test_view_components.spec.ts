import Vue from "vue";
import Vuex from "vuex";
import VueRouter from "vue-router";
import APISpec from "./openapi.json";
import flushPromises from "flush-promises";

import { createLocalVue, mount, shallowMount } from "@vue/test-utils";

import SystemSpec from "@/views/SystemSpec.vue";

import { domain, clientId, audience } from "../../auth_config.json";
import { authGuard } from "../../src/auth/authGuard";
import * as auth from "../../src/auth/auth";

import { System } from "@/types/System";
import { APIValidator } from "@/types/validation/Validator";

const mockedAuthInstance = jest.spyOn(auth, "getInstance");

const user = {
  email: "testing@solaforecastarbiter.org",
  email_verified: true,
  sub: "auth0|5fa9596ccf64f9006e841a3a"
};

const $auth = {
  isAuthenticated: true,
  loading: false,
  user: user,
  logout: jest.fn(),
  loginWithRedirect: jest.fn(),
  getTokenSilently: jest.fn().mockReturnValue("Token")
};

// @ts-expect-error
mockedAuthInstance.mockImplementation(() => $auth);

const localVue = createLocalVue();

const $validator = new APIValidator();
$validator.getAPISpec = jest.fn().mockResolvedValue(APISpec);

const $router = {
  push: jest.fn()
};
const mocks = {
  $auth,
  $validator,
  $router
};

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
  jest.clearAllMocks();
});
import ModelField from "@/components/ModelField.vue";
import InvertersView from "@/components/Inverters.vue";
Vue.component("model-field", ModelField);
Vue.component("inverters-view", ModelField);

describe("Test SystemSpec view", () => {
  it("Test load system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
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
      mocks
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
      mocks
    });
    await flushPromises();
    expect(wrapper.vm.$data.errorState).toBe(true);
  });
  it("Test save system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      mocks
    });
    await flushPromises();
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(wrapper.vm.$data.apiErrors).toEqual({});
    expect($router.push).toHaveBeenCalledWith("/systems");
    expect(fetch).toHaveBeenCalledWith("/api/systems/", expect.anything());
  });
  it("Test save existing system", async () => {
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      propsData: {
        systemId: "banana"
      },
      mocks
    });
    await flushPromises();
    expect(wrapper.vm.$data.system).toEqual(system);
    expect(fetch).toHaveBeenCalledWith(
      "/api/systems/banana",
      expect.anything()
    );
  });

  it("Test save system failure", async () => {
    fetchMock.ok = false;
    const wrapper = shallowMount(SystemSpec, {
      localVue,
      mocks
    });
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect($router.push).not.toHaveBeenCalled();
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
      mocks
    });
    await flushPromises();
    const saveBtn = wrapper.find("button.save-system");
    saveBtn.trigger("click");
    await flushPromises();
    expect(wrapper.vm.$data.apiErrors).toEqual({
      error: "API responded with status code: 500"
    });
    expect($router.push).not.toHaveBeenCalled();
  });
});
