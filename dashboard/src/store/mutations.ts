import { StoredSystem } from "../types/System";
import { State } from "./state";

export const mutations = {
  updateSystemsList(state: State, systems: Record<string, StoredSystem>) {
    state.systems = systems;
    state.loading = false;
  },
  setLoading(state: State) {
    state.loading = true;
  }
};
