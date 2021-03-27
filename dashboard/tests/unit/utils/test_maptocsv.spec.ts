import { mapToCSV } from "@/utils/mapToCSV";

const testCSVObject = [
  { t: "2020-01-01T00:00Z", glob: 1, dir: 4 },
  { t: "2020-01-01T01:00Z", glob: 2, dir: 3 },
  { t: "2020-01-01T02:00Z", glob: 3, dir: 2 },
  { t: "2020-01-01T03:00Z", glob: 4, dir: 1 }
];

const testCSVNoHeaders = [
  ["2020-01-01T00:00Z", 1, 4],
  ["2020-01-01T01:00Z", 2, 3],
  ["2020-01-01T02:00Z", 3, 2],
  ["2020-01-01T03:00Z", 4, 1]
];

describe("test csv mapping", () => {
  it("test mapping", () => {
    const testMapping = {
      time: { csv_header: { header: "t", header_index: 0 } },
      dni: { csv_header: { header: "dir", header_index: 1 } }
    };
    expect(mapToCSV(testCSVObject, testMapping)).toEqual(
      `time,dni\r\n2020-01-01T00:00Z,4\r\n2020-01-01T01:00Z,3\r\n2020-01-01T02:00Z,2\r\n2020-01-01T03:00Z,1`
    );
  });
  it("test mapping with unit conversion", () => {
    const testMapping = {
      time: { csv_header: { header: "t", header_index: 0 } },
      performance: {
        csv_header: { header: "dir", header_index: 1 },
        units: "kW"
      }
    };
    expect(mapToCSV(testCSVObject, testMapping)).toEqual(
      `time,performance\r\n2020-01-01T00:00Z,4000\r\n2020-01-01T01:00Z,3000\r\n2020-01-01T02:00Z,2000\r\n2020-01-01T03:00Z,1000`
    );
  });
  it("test mapping without headers", () => {
    const testMapping = {
      time: { csv_header: { header_index: 0 } },
      dni: { csv_header: { header_index: 2 } }
    };
    expect(mapToCSV(testCSVNoHeaders, testMapping)).toEqual(
      `time,_missing_col_1,dni\r\n2020-01-01T00:00Z,1,4\r\n2020-01-01T01:00Z,2,3\r\n2020-01-01T02:00Z,3,2\r\n2020-01-01T03:00Z,4,1`
    );
  });
});
