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

const mocks = {
  $auth,
  $validator
};

const system = new System({ name: "Test" });

let fetchMock: any = {};

global.fetch = jest.fn(() => Promise.resolve(fetchMock));

beforeAll(() => {
  $validator.init();
  // reset the mocked response so each test can alter as needed.
  fetchMock = {
    ok: true,
    json: () => Promise.resolve({ definition: system })
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
});
