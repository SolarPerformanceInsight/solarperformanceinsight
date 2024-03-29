import { getUnitConverter, getUnitOptions } from "@/utils/unitConversion";

describe("Test power conversion", () => {
  it("kW => W", () => {
    const expected = [
      [1, 1000],
      [10, 10000],
      [0.25, 250],
      [0.001, 1]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("kW", "W");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("MW => W", () => {
    const expected = [
      [1, 1000000],
      [10, 10000000],
      [0.25, 250000],
      [0.001, 1000]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("MW", "W");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("GW => W", () => {
    const expected = [
      [1, 1000000000],
      [10, 10000000000],
      [0.25, 250000000],
      [0.001, 1000000]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("GW", "W");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("W => MW", () => {
    const expected = [
      [1000000, 1],
      [10000000, 10],
      [250000, 0.25],
      [1000, 0.001],
      [5, 0.000005]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("W", "MW");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("GW => MW", () => {
    const expected = [
      [1, 1000],
      [1.5, 1500],
      [2, 2000],
      [0.025, 25]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("GW", "MW");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("W/m^2 => MW", () => {
    const converter = getUnitConverter("W/m^2", "MW");
    expect(converter).toBe(null);
  });
  it("DNE", () => {
    const converter = getUnitConverter("DNE", "DNE/m^2");
    expect(converter).toBe(null);
  });
  it("kWh => Wh", () => {
    const expected = [
      [1, 1000],
      [10, 10000],
      [0.25, 250],
      [0.001, 1]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("kWh", "Wh");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("kW/m^2 => W/m^2", () => {
    const expected = [
      [1, 1000],
      [10, 10000],
      [0.25, 250],
      [0.001, 1]
    ];
    for (const results of expected) {
      const converter = getUnitConverter("kW/m^2", "W/m^2");
      // @ts-expect-error
      expect(converter(results[0])).toBeCloseTo(results[1]);
    }
  });
  it("Wh/m^2 => kWh/m^2", () => {
    const converter = getUnitConverter("Wh/m^2", "kWh/m^2");
    // @ts-expect-error
    expect(converter(1000)).toBeCloseTo(1);
  });
  it("null converter", () => {
    const converter = getUnitConverter("W", "W");
    expect(converter).toBe(null);
  });
  it("getUnitOptions", () => {
    const unitOpts = getUnitOptions("performance");
    expect(unitOpts).toEqual(["W", "kW", "MW", "GW"]);
  });
});
