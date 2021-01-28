import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

const testSystem = new System({
  name: "Test System",
  inverters: [
    new Inverter({
      name: "Inverter 1",
      arrays: [
        new PVArray({ name: "Array 1 Inverter 1" }),
        new PVArray({ name: "Array 1 Inverter 1" })
      ]
    }),
    new Inverter({
      name: "Inverter 2",
      arrays: [
        new PVArray({ name: "Array 1 Inverter 2" }),
        new PVArray({ name: "Array 1 Inverter 2" })
      ]
    })
  ]
});

describe("Test indexing into system", () => {
  it("get root system", () => {
    expect(indexSystemFromSchemaPath(testSystem, "/")).toEqual(testSystem);
  });
  it("get array 1 inv 1 with string", () => {
    expect(
      indexSystemFromSchemaPath(testSystem, "/inverters/0/arrays/0")
    ).toEqual(testSystem.inverters[0].arrays[0]);
  });
  it("get array 1 inv 1 with array", () => {
    expect(
      indexSystemFromSchemaPath(testSystem, ["inverters", "0", "arrays", "0"])
    ).toEqual(testSystem.inverters[0].arrays[0]);
  });
  it("test empty index string error", () => {
    expect(() => {
      indexSystemFromSchemaPath(testSystem, "");
    }).toThrow();
  });
  it("test empty index array error", () => {
    expect(() => {
      indexSystemFromSchemaPath(testSystem, []);
    }).toThrow();
  });
  it("test invalid index string error", () => {
    expect(() => {
      indexSystemFromSchemaPath(testSystem, "/inverters/4/arrays/1");
    }).toThrow();
  });
  it("test invalid index undef system", () => {
    expect(() => {
      // @ts-expect-error
      indexSystemFromSchemaPath(testSystem.pony, "/inverters/4/arrays/1");
    }).toThrow();
  });
});
