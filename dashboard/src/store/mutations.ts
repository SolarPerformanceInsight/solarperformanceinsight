import Vuex from "vuex";
import { System } from "../types/System";
import { state, State } from "./state";

export const mutations = {
  updateSystemsList(state: State, systems: Array<System>) {
    state.systems = systems;
  }
};
