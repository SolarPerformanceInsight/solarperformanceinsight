import { getVariableUnits } from "@/utils/units";

describe("Test get variable units", () => {
  it("get units", () => {
    expect(getVariableUnits("ratio")).toBe("%");
  });
  it("get units unitless", () => {
    expect(getVariableUnits("month")).toBe("");
  });
  it("get units dne", () => {
    console.error = jest.fn();
    expect(getVariableUnits("smoosh")).toBe("");
    expect(console.error).toHaveBeenCalled();
  });
});
