import { getVariableDisplayName } from "@/utils/displayNames";
describe("test getVariableDisplay", () => {
  it("exists", () => {
    expect(getVariableDisplayName("time")).toBe("Timestamp");
  });
  it("DNE", () => {
    console.error = jest.fn();
    expect(getVariableDisplayName("WOW")).toBe("WOW");
    expect(console.error).toHaveBeenCalled();
  });
});
