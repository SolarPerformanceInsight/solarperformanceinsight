import { state } from "./state";
import { mutations } from "./mutations";
import { actions } from "./actions";

export const spiStore = {
  state: state,
  mutations: mutations,
  actions: actions
};

export type SpiStore = typeof spiStore;
