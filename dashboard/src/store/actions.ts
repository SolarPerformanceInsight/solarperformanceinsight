import { System } from "../types/System";

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
    const systemMapping: Record<string, System> = {};
    for (const system of systemlist) {
      systemMapping[system.system_id] = system as System;
    }
    context.commit("updateSystemsList", systemMapping);
  }
};
