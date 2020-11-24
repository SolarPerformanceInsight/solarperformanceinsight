import Vuex from "vuex";
import DemoSystems from "../types/demo/systems";
import { System } from "../types/System";
import { state, State } from "./state";
import { mutations } from "./mutations";
import { actions } from "./actions";

export const spiStore = {
  state: state,
  mutations: mutations,
  actions: actions,
};
