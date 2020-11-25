import Vuex from "vuex";
import { System } from "../types/System";
import { state, State } from "./state";

export const mutations = {
  updateSystemsList(state: State, systems: Record<string, System>) {
    state.systems = systems;
    state.loading = false;
  },
  setLoading(state: State) {
    state.loading = true;
  }
};
