import parseCSV from "@/utils/parseCSV";

const testCSV = `a,b,c,d
1,2,3,4
5,6,7,8
9,10,11,12`;

describe("Test parseCSV", () => {
  it("parse a csv", () => {
    const result = parseCSV(testCSV);
    expect(result.data).toEqual([
      {a: 1, b: 2, c: 3, d: 4},
      {a: 5, b: 6, c: 7, d: 8},
      {a: 9, b: 10, c: 11, d: 12},
    ]);
  });
  it("preview a csv", () => {
    const result = parseCSV(testCSV, 2);
    expect(result.data).toEqual([
      {a: 1, b: 2, c: 3, d: 4},
      {a: 5, b: 6, c: 7, d: 8},
    ]);
  });
  it("Test bad csv", () => {
    let error: any;
    const result = parseCSV("a,b,c\n1");
    expect(result.errors).toEqual([
      {
        "code": "TooFewFields",
        "message": "Too few fields: expected 3 fields but parsed 1",
        "row": 0,
        "type": "FieldMismatch"
      }
    ]);
  });
});
