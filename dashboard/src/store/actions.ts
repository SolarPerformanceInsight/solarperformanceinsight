import Store from "vuex";
import { System } from "../types/System";

export const actions = {
  async fetchSystems(context: any) {
    // @ts-expect-error
    const token = await this._vm.$auth.getTokenSilently();
    const systemlist = await fetch("/api/systems/", {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      })
    }).then(response => response.json());
    context.commit("updateSystemsList", systemlist as Array<System>);
  }
};
