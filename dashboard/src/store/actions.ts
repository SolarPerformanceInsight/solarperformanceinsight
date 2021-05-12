/* istanbul ignore file */

import { StoredSystem } from "../types/System";

export const actions = {
  async fetchSystems(context: any) {
    context.commit("setLoading");
    // @ts-expect-error
    const token = await this._vm.$auth.getTokenSilently();
    const systemlist = await fetch("/api/systems/", {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      })
    }).then(response => response.json());
    const systemMapping: Record<string, StoredSystem> = {};
    for (const system of systemlist) {
      systemMapping[system.object_id] = system as StoredSystem;
    }
    context.commit("updateSystemsList", systemMapping);
  }
};
