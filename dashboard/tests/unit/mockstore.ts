import { actions } from "@/store/actions";
import { spiStore } from "@/store/store";
import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

const storedSystems = {
  someuuid: new StoredSystem({
    object_id: "someuuid",
    object_type: "system",
    created_at: "before",
    modified_at: "now",
    definition: new System({
      name: "Super System",
      inverters: [
        new Inverter({
          arrays: [new PVArray({})]
        })
      ]
    })
  })
};

// @ts-expect-error
jest.spyOn(actions, "fetchSystems").mockImplementation((context: any) => {
  context.commit("updateSystemsList", storedSystems);
});

spiStore.state.systems = {};

beforeAll(() => {
  spiStore.state.systems = {};
});

const storeObject = spiStore;

export { storeObject };
