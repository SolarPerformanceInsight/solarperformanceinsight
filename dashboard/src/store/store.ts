import Vuex from "vuex";
import DemoSystems from "../types/demo/systems";
import { System } from "../types/System";
import { state, State } from "./state";
import { mutations } from "./mutations";

export const spiStore = {
  state: state,
  mutations: mutations,
};
