import convertPower from "@/utils/powerConversion";

describe("Test power conversion", () => {
  it("kW => W", () => {
    const expected = [
      [1, 1000],
      [10, 10000],
      [.25, 250],
      [.001, 1]
    ];
    for (const results of expected) {
      expect(
        convertPower(
          "kW",
          "W",
          results[0]
        )
      ).toBeCloseTo(results[1]);
    }
  });
  it("MW => W", () => {
    const expected = [
      [1, 1000000],
      [10, 10000000],
      [.25, 250000],
      [.001, 1000]
    ];
    for (const results of expected) {
      expect(
        convertPower(
          "MW",
          "W",
          results[0]
        )
      ).toBeCloseTo(results[1]);
    }
  });
  it("GW => W", () => {
    const expected = [
      [1, 1000000000],
      [10, 10000000000],
      [.25, 250000000],
      [.001, 1000000]
    ];
    for (const results of expected) {
      expect(
        convertPower(
          "GW",
          "W",
          results[0]
        )
      ).toBeCloseTo(results[1]);
    }
  });
  it("W => MW", () => {
    const expected = [
      [1000000, 1],
      [10000000, 10],
      [250000, .25],
      [1000, .001],
      [5, .000005]
    ];
    for (const results of expected) {
      expect(
        convertPower(
          "W",
          "MW",
          results[0]
        )
      ).toBeCloseTo(results[1]);
    }
  });
});
