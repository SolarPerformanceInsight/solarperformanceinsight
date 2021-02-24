import convertPower from "@/utils/powerConversion";

describe("Test power conversion", () => {
  it("kW => W", () => {
    const expected = [
      [1, 1000],
      [10, 10000],
      [0.25, 250],
      [0.001, 1]
    ];
    for (const results of expected) {
      expect(convertPower("kW", "W", results[0])).toBeCloseTo(results[1]);
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
      expect(convertPower("MW", "W", results[0])).toBeCloseTo(results[1]);
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
      expect(convertPower("GW", "W", results[0])).toBeCloseTo(results[1]);
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
      expect(convertPower("W", "MW", results[0])).toBeCloseTo(results[1]);
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
      expect(convertPower("GW", "MW", results[0])).toBeCloseTo(results[1]);
    }
  });
});
