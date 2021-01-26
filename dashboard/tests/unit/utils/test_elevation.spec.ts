import { getElevation } from "@/utils/elevation";

let mockResponse: any = {};
let fetchMock: any = {};
global.fetch = jest.fn(() => Promise.resolve(fetchMock));

beforeEach(() => {
  mockResponse = {
    USGS_Elevation_Point_Query_Service: {
      Elevation_Query: {
        Data_Source: "3DEP 1/3 arc-second",
        Elevation: 722.68,
        Units: "Meters",
        x: -110.9747,
        y: 32.2226
      }
    }
  };
  fetchMock = {
    ok: true,
    json: jest.fn().mockResolvedValue(mockResponse),
    status: 200
  };
  jest.clearAllMocks();
});

describe("test elevation", () => {
  it("test success", async () => {
    const el = await getElevation(32.2226, -110.9747);
    expect(el).toBe(722.68);
  });
  it("test missing value", async () => {
    mockResponse.USGS_Elevation_Point_Query_Service.Elevation_Query.Elevation =
      "-1000000";
    expect(getElevation(32.2226, -110.9747)).rejects.toThrow();
  });
  it("test request failure", async () => {
    fetchMock.ok = false;
    expect(getElevation(32.2226, -110.9747)).rejects.toThrow();
  });
});
