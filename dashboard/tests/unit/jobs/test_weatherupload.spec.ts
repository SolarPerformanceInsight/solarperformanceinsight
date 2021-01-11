import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import WeatherCSVMapper from "@/components/jobs/WeatherCSVMapper.vue";
import WeatherUpload from "@/components/jobs/WeatherUpload.vue";

import * as Jobs from "@/api/jobs";
import * as auth from "@/auth/auth";

// test prop constants
const testJob = {
  object_id: "e1772e64-43ac-11eb-92c2-f4939feddd82",
  object_type: "job",
  created_at: "2020-12-11T19:52:00+00:00",
  modified_at: "2020-12-11T19:52:00+00:00",
  definition: {
    system_definition: {
      name: "Test PV System",
      latitude: 33.98,
      longitude: -115.323,
      elevation: 2300,
      inverters: [
        {
          name: "Inverter 1",
          make_model: "ABB__MICRO_0_25_I_OUTD_US_208__208V_",
          inverter_parameters: {
            Pso: 2.08961,
            Paco: 250,
            Pdco: 259.589,
            Vdco: 40,
            C0: -0.000041,
            C1: -0.000091,
            C2: 0.000494,
            C3: -0.013171,
            Pnt: 0.075
          },
          losses: {},
          arrays: [
            {
              name: "Array 1",
              make_model: "Canadian_Solar_Inc__CS5P_220M",
              albedo: 0.2,
              modules_per_string: 7,
              strings: 5,
              tracking: {
                tilt: 20,
                azimuth: 180
              },
              temperature_model_parameters: {
                u_c: 29,
                u_v: 0,
                eta_m: 0.1,
                alpha_absorption: 0.9
              },
              module_parameters: {
                alpha_sc: 0.004539,
                gamma_ref: 1.2,
                mu_gamma: -0.003,
                I_L_ref: 5.11426,
                I_o_ref: 8.10251e-10,
                R_sh_ref: 381.254,
                R_s: 1.06602,
                R_sh_0: 400,
                cells_in_series: 96
              }
            }
          ],
          airmass_model: "kastenyoung1989",
          aoi_model: "no_loss",
          clearsky_model: "ineichen",
          spectral_model: "no_loss",
          transposition_model: "haydavies"
        }
      ]
    },
    parameters: {
      system_id: "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
      job_type: {
        calculate: "predicted performance"
      },
      time_parameters: {
        start: "2020-01-01T00:00:00+00:00",
        end: "2020-12-31T23:59:59+00:00",
        step: "15:00",
        timezone: "UTC"
      },
      weather_granularity: "array",
      irradiance_type: "poa",
      temperature_type: "module"
    }
  },
  status: {
    status: "incomplete",
    last_change: "2020-12-11T20:00:00+00:00"
  },
  data_objects: [
    {
      object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
      object_type: "job_data",
      created_at: "2020-12-11T19:52:00+00:00",
      modified_at: "2020-12-11T19:52:00+00:00",
      definition: {
        schema_path: "/inverters/0/arrays/0",
        type: "original weather data",
        present: false,
        data_columns: [
          "time",
          "poa_global",
          "poa_direct",
          "poa_diffuse",
          "module_temperature"
        ]
      }
    }
  ]
};

const headers = ["timestamp", "global", "direct", "diffuse"];

const usedHeaders: Array<string> = [];

const testCSV = "a,b,c,d,e\n1,2,3,4,5";

const testMapping = {
  "/inverters/0/arrays/0": {
    time: "a",
    poa_global: "b",
    poa_direct: "c",
    poa_diffuse: "d",
    module_temperature: "e"
  }
};

// vue test setup
const localVue = createLocalVue();

Vue.component("weather-csv-mapper", WeatherCSVMapper);

const user = {
  email: "testing@solaforecastarbiter.org",
  email_verified: true,
  sub: "auth0|5fa9596ccf64f9006e841a3a"
};

const $auth = {
  isAuthenticated: true,
  loading: false,
  user: user,
  logout: jest.fn(),
  loginWithRedirect: jest.fn(),
  getTokenSilently: jest.fn().mockReturnValue("Token")
};

const mockedAuthInstance = jest.spyOn(auth, "getInstance");

// @ts-expect-error
mockedAuthInstance.mockImplementation(() => $auth);

const mocks = {
  $auth
};

const mockedDataPost = jest.spyOn(Jobs, "addData");

const mockJobResponse = {
  ok: true,
  status: 200
};
mockedDataPost.mockImplementation(jest.fn().mockResolvedValue(mockJobResponse));

beforeEach(() => jest.clearAllMocks());

describe("Test Weather Upload", () => {
  it("Test getters and init", async () => {
    const propsData = {
      jobId: testJob.object_id,
      weather_granularity: testJob.definition.parameters.weather_granularity,
      irradiance_type: testJob.definition.parameters.irradiance_type,
      temperature_type: testJob.definition.parameters.temperature_type,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects
    };
    const weatherUpload = mount(WeatherUpload, {
      localVue,
      propsData
    });
    expect(weatherUpload.vm.$data.required).toEqual([
      "time",
      "poa_global",
      "poa_direct",
      "poa_diffuse",
      "module_temperature"
    ]);
    // @ts-expect-error
    expect(weatherUpload.vm.totalMappings).toBe(5);
  });
  it("Test store and map csv", async () => {
    const propsData = {
      jobId: testJob.object_id,
      weather_granularity: testJob.definition.parameters.weather_granularity,
      irradiance_type: testJob.definition.parameters.irradiance_type,
      temperature_type: testJob.definition.parameters.temperature_type,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects
    };
    const weatherUpload = mount(WeatherUpload, {
      localVue,
      propsData,
      mocks
    });
    expect(weatherUpload.findComponent(WeatherCSVMapper).exists()).toBe(false);
    // @ts-expect-error
    weatherUpload.vm.storeCSV(testCSV);
    await flushPromises();
    expect(weatherUpload.findComponent(WeatherCSVMapper).exists()).toBe(true);
    expect(weatherUpload.vm.$data.csvData).toEqual([
      {
        a: 1,
        b: 2,
        c: 3,
        d: 4,
        e: 5
      }
    ]);
    // @ts-expect-error
    weatherUpload.vm.processMapping(testMapping);
    expect(weatherUpload.vm.$data.mapping).toEqual(testMapping);

    // @ts-expect-error
    await weatherUpload.vm.uploadData();
    await flushPromises();
    expect(mockedDataPost).toHaveBeenCalledWith(
      "Token",
      testJob.object_id,
      testJob.data_objects[0].object_id,
      testJob.data_objects[0].definition.data_columns.join(",") +
        "\r\n1,2,3,4,5"
    );
  });
});
