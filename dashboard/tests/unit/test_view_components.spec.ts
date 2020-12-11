import Vue from "vue";
import Vuex from "vuex";
import VueRouter from "vue-router";
import APISpec from "./openapi.json";

import { createLocalVue, mount } from "@vue/test-utils";

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
  loginWithRedirect: jest.fn()
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

beforeAll(() => {
  $validator.init();
});

describe("Test SystemSpec view", () => {
  it("Test new system", async () => {
    const wrapper = mount(SystemSpec, {
      mocks
    });
    await Vue.nextTick();
    expect(wrapper.props("system")).toEqual(new System({}));
  });
});
