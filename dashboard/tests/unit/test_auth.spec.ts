import Vue from "vue";
import Vuex from "vuex";
import VueRouter from "vue-router";

import { createLocalVue, mount } from "@vue/test-utils";

import Home from "@/views/Home.vue";
import App from "@/App.vue";
import router from "@/router";

import { $auth } from "./mockauth";
import { $validator } from "./mockvalidator";

import { User } from "@/auth/User";

const localVue = createLocalVue();

const mocks = {
  $auth,
  $validator
};

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
    jest.clearAllMocks();
    // @ts-expect-error
    if (router.history.current.path != "/") {
      router.push({ name: "Home" });
    }
  });
  it("unauthenticated home", async () => {
    const home = mount(Home, {
      store,
      localVue,
      router,
      mocks
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
    jest.clearAllMocks();
    // @ts-expect-error
    if (router.history.current.path != "/") {
      router.push({ name: "Home" });
    }
  });
  it("authenticated home", async () => {
    const home = mount(Home, {
      store,
      localVue,
      router,
      mocks
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

describe("Test authguard", () => {
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
    jest.clearAllMocks();
    // @ts-expect-error
    if (router.history.current.path != "/") {
      router.push({ name: "Home" });
    }
  });

  it("test unauthenticated access to protected route", async () => {
    $auth.isAuthenticated = false;
    const view = mount(App, {
      store,
      localVue,
      router,
      mocks
    });
    expect(view.find("p").text()).toMatch(/Welcome to the solar/);
    expect($auth.loginWithRedirect).not.toHaveBeenCalled();
    router.push({ name: "Systems" });
    await Vue.nextTick();
    expect($auth.loginWithRedirect).toHaveBeenCalled();
    // assert view has not changed since loginWithRedirect is mocked and does
    // nothing
    expect(view.find("p").text()).toMatch(/Welcome to the solar/);
  });
  it("test authenticated access to protected route", async () => {
    $auth.isAuthenticated = true;
    const view = mount(App, {
      store,
      localVue,
      router,
      mocks
    });
    expect(view.find("p").text()).toMatch(/Successfully logged in/);
    expect($auth.loginWithRedirect).not.toHaveBeenCalled();
    router.push({ name: "Systems" });
    await Vue.nextTick();
    expect($auth.loginWithRedirect).not.toHaveBeenCalled();
    // Assert view at new path is rendered
    expect(view.find("h1").text()).toMatch(/Systems/);
  });
});

describe("test user", () => {
  it("instantiate a user object", () => {
    const user = {
      sub: "auth0|somestuff",
      names: "names",
      nickname: "rick",
      picture: "http://www.photobucket.com/rickvacation",
      updated_at: "2222-22-22T22:22:22-10:00"
    };
    const expected = {
      sub: "auth0|somestuff",
      provider: "auth0",
      id: "somestuff",
      names: "names",
      nickname: "rick",
      picture: "http://www.photobucket.com/rickvacation",
      updated_at: "2222-22-22T22:22:22-10:00"
    };
    const instance = new User(user);
    expect(instance).toEqual(expected);
  });
  it("instantiate a user object from falsey", () => {
    // @ts-expect-error
    expect(new User(null)).toEqual({});
  });
});
