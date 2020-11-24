import Vuex from "vuex";
import DemoSystems from "../types/demo/systems";
import { System } from "../types/System";
import { state, State } from "./state";

export const mutations = {
  upadeSystemsList(state: State){
    // TODO: get a fresh system list from the api
    console.log("Should update systems list");
  }
};
