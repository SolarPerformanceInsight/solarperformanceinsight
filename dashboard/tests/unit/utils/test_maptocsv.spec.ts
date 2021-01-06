import mapToCSV from "@/utils/mapToCSV";

const testCSVObject = {
  t: [
    "2020-01-01T00:00Z",
    "2020-01-01T01:00Z",
    "2020-01-01T02:00Z",
    "2020-01-01T03:00Z"
  ],
  glob: [1, 2, 3, 4],
  dir: [4, 3, 2, 1]
};

const testMapping = {
  time: "t",
  dni: "dir"
};
describe("test csv mapping", () => {
  it("test mapping", () => {
    expect(mapToCSV(testCSVObject, testMapping)).toEqual(
      `time,dni
2020-01-01T00:00Z,4
2020-01-01T01:00Z,3
2020-01-01T02:00Z,2
2020-01-01T03:00Z,1
`
    );
  });
});
