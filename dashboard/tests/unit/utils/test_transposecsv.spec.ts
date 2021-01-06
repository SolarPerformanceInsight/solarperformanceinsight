import transposeCSV from "@/utils/transposeCSV";

const testCSV = `a,b,c,d
1,2,3,4
5,6,7,8
9,10,11,12`;

describe("Test transposeCSV", () => {
  it("transpose a csv", async () => {
    expect(await transposeCSV(testCSV)).toEqual({
      a: ["1", "5", "9"],
      b: ["2", "6", "10"],
      c: ["3", "7", "11"],
      d: ["4", "8", "12"]
    });
  });
  it("Test bad csv", async () => {
    let error: any;
    try {
      await transposeCSV("a,b,c\n1");
    } catch (e) {
      error = e;
    }
    expect(error.name).toBe("CSV Parse Error");
    expect(error.err).toBe("column_mismatched");
  });
});
