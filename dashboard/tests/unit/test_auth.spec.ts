import { createLocalVue, mount } from "@vue/test-utils";
import Vuex from "vuex";
import VueRouter from "vue-router";
import { SpiStore } from "@/store/store";
import { domain, clientId, audience } from "../../auth_config.json";
import Home from "@/views/Home.vue";

const user = {
  email: "testing@solaforecastarbiter.org",
  email_verified: true,
  sub: "auth0|5fa9596ccf64f9006e841a3a"
};

const router = { push: jest.fn() };
const localVue = createLocalVue();

const $auth = {
  isAuthenticated: true,
  loading: false,
  user: user,
  logout: jest.fn(),
  loginWithRedirect: jest.fn()
};

function resetAuthMocks() {
  $auth.logout.mockClear();
  $auth.loginWithRedirect.mockClear();
}

localVue.use(Vuex);
localVue.use(VueRouter);

describe("Tests authenticated routes", () => {
  let actions: any;
  let store: any;
  let state: any;
  beforeEach(() => {
    actions = {
      fetchSystems: jest.fn()
    };
    state = {
      systems: []
    };
    store = new Vuex.Store({
      state,
      actions
    });
    $auth.isAuthenticated = false;
    resetAuthMocks();
  });
  it("unauthenticated home", async () => {
    const home = mount(Home, {
      store,
      localVue,
      mocks: {
        $auth
      }
    });
    expect(home.find("p").text()).toMatch(/Welcome to the solar/);
    const button = home.find("button");
    expect(button.text()).toMatch(/Log in/);
    expect($auth.loginWithRedirect).not.toHaveBeenCalled();
    await button.trigger("click");
    expect($auth.loginWithRedirect).toHaveBeenCalled();
    expect($auth.logout).not.toHaveBeenCalled();
    expect(actions.fetchSystems).not.toHaveBeenCalled();
  });
});

describe("Tests authenticated routes", () => {
  let actions: any;
  let store: any;
  let state: any;
  beforeEach(() => {
    actions = {
      fetchSystems: jest.fn()
    };
    state = {
      systems: []
    };
    store = new Vuex.Store({
      state,
      actions
    });
    $auth.isAuthenticated = true;
    resetAuthMocks();
  });
  it("authenticated home", async () => {
    const home = mount(Home, {
      store,
      localVue,
      mocks: {
        $auth
      }
    });
    expect(home.find("p").text()).toMatch(/Successfully logged in./);
    const button = home.find("button");
    expect(button.text()).toMatch(/Log out/);
    expect($auth.logout).not.toHaveBeenCalled();
    await button.trigger("click");
    expect($auth.logout).toHaveBeenCalled();
    expect($auth.loginWithRedirect).not.toHaveBeenCalled();
    expect(actions.fetchSystems).not.toHaveBeenCalled();
  });
});
