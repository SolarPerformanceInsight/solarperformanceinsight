import mapToCSV from "@/utils/mapToCSV";

const testCSVObject = [
  { t: "2020-01-01T00:00Z", glob: 1, dir: 4 },
  { t: "2020-01-01T01:00Z", glob: 2, dir: 3 },
  { t: "2020-01-01T02:00Z", glob: 3, dir: 2 },
  { t: "2020-01-01T03:00Z", glob: 4, dir: 1 }
];

const testMapping = {
  time: "t",
  dni: "dir"
};
describe("test csv mapping", () => {
  it("test mapping", () => {
    expect(mapToCSV(testCSVObject, testMapping)).toEqual(
      `time,dni\r\n2020-01-01T00:00Z,4\r\n2020-01-01T01:00Z,3\r\n2020-01-01T02:00Z,2\r\n2020-01-01T03:00Z,1`
    );
  });
});
