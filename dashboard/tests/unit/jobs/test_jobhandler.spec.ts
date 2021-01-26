import Vue from "vue";
import VueRouter from "vue-router";
import flushPromises from "flush-promises";
import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import JobHandler from "@/components/jobs/JobHandler.vue";
import JobParams from "@/components/jobs/parameters/JobParams.vue";
import CalculateJobParams from "@/components/jobs/parameters/CalculateJobParams.vue";
import CompareJobParams from "@/components/jobs/parameters/CompareJobParams.vue";
import CalculatePRJobParams from "@/components/jobs/parameters/CalculatePRJobParams.vue";
import TimeParameters from "@/components/jobs/parameters/TimeParameters.vue";
import CSVUpload from "@/components/jobs/CSVUpload.vue";

import * as Jobs from "@/api/jobs";
import { mockedAuthInstance, $auth } from "../mockauth";
import router from "@/router";

import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import { SingleAxisTrackingParameters } from "@/types/Tracking";

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
      granularity: "array",
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
        present: false
      }
    }
  ]
};

const headers = ["timestamp", "global", "direct", "diffuse"];

const usedHeaders: Array<string> = [];

const required = ["time", "ghi", "dni", "dhi"];

// vue test setup
const localVue = createLocalVue();
localVue.use(VueRouter);

// Mock jobs api wrapper function
const mockedJobRead = jest.spyOn(Jobs, "read");

const mockJobResponse = {
  ok: true,
  json: jest.fn().mockResolvedValue(testJob),
  status: 200
};
mockedJobRead.mockImplementation(jest.fn().mockResolvedValue(mockJobResponse));

const mocks = {
  $auth
};

// Mock global fetch to test system loading
const fetchBody = new StoredSystem({
  object_id: "uuid",
  object_type: "system",
  created_at: "2021-01-01T00:00+00:00",
  modified_at: "2021-01-01T00:00+00:00",
  definition: new System({
    name: "New System",
    inverters: [
      new Inverter({
        name: "New Inverter",
        arrays: [new PVArray({ name: "New Array" })]
      })
    ]
  })
});

const fetchMock = {
  ok: true,
  json: jest.fn().mockResolvedValue(fetchBody),
  status: 200
};

global.fetch = jest.fn().mockResolvedValue(fetchMock);

beforeEach(() => {
  jest.clearAllMocks();
  // Reset the mocked fetch to the system response
  fetchMock.ok = true;
  fetchMock.json = jest.fn().mockResolvedValue(fetchBody);
  fetchMock.status = 200;
  mockJobResponse.ok = true;
  mockJobResponse.json = jest.fn().mockResolvedValue(testJob);
  mockJobResponse.status = 200;

  // @ts-expect-error
  if (router.history.current.path != "/") {
    router.push("/");
  }
});

Vue.component("csv-upload", CSVUpload);
Vue.component("calculate-job-params", CalculateJobParams);
Vue.component("compare-job-params", CompareJobParams);
Vue.component("calculatepr-job-params", CalculatePRJobParams);
Vue.component("time-parameters", TimeParameters);

describe("Test JobHandler", () => {
  it("load calculate job", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    expect(mockedJobRead).toHaveBeenLastCalledWith("Token", testJob.object_id);
    // @ts-expect-error
    expect(handler.vm.jobType).toEqual({
      calculate: "predicted performance"
    });
    expect(
      // @ts-expect-error
      handler.vm.filteredDataObjects("original weather data")
    ).toEqual(testJob.data_objects);
    expect(
      // @ts-expect-error
      handler.vm.filteredDataObjects("predicted performance data")
    ).toEqual([]);
    expect(handler.findComponent(CSVUpload).exists()).toBe(true);
    expect(handler.find("b").text()).toBe("Upload Original Weather Data");
  });
  it("test job not found", async () => {
    mockJobResponse.ok = false;
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    expect(handler.find("div.errors").text()).toBe(
      '{\n  "error": "Job not found."\n}'
    );
  });
  it("load calculation setup", async () => {
    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculate"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    const jobparams = handler.findComponent(JobParams);
    expect(jobparams.findComponent(CalculateJobParams).exists()).toBe(true);
    // Strip whitespace before comparison, template renders this whitespace
    // which is appropriately ignored by browsers
    expect(
      handler
        .find("h1")
        .text()
        .replace(/\s/g, "")
    ).toBe(`CalculatePerformanceFor:NewSystem`);
    // @ts-expect-error
    expect(handler.vm.jobType).toBe(null);
  });
  it("load compare setup", async () => {
    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "compare"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    const jobparams = handler.findComponent(JobParams);
    expect(jobparams.findComponent(CompareJobParams).exists()).toBe(true);
    // Strip whitespace before comparison, template renders this whitespace
    // which is appropriately ignored by browsers
    expect(
      handler
        .find("h1")
        .text()
        .replace(/\s/g, "")
    ).toBe(`ComparePerformanceFor:NewSystem`);
  });
  it("load calculate pr setup", async () => {
    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculatepr"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    const jobparams = handler.findComponent(JobParams);
    expect(jobparams.findComponent(CalculatePRJobParams).exists()).toBe(true);
    // Strip whitespace before comparison, template renders this whitespace
    // which is appropriately ignored by browsers
    expect(
      handler
        .find("h1")
        .text()
        .replace(/\s/g, "")
    ).toBe(`CalculateWeatherAdjustedPerformanceRatioFor:NewSystem`);
  });
  it("test load system failure", async () => {
    fetchMock.ok = false;

    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculate"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    expect(handler.find("div.errors").text()).toBe(
      '{\n  "error": "System not found."\n}'
    );
  });
  it("test load system failure", async () => {
    fetchMock.ok = false;

    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculate"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    expect(handler.find("div.errors").text()).toBe(
      '{\n  "error": "System not found."\n}'
    );
  });
  it("test job creation redirection", async () => {
    fetchMock.ok = false;

    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculate"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    jest.spyOn(router, "push");
    await flushPromises();
    // @ts-expect-error
    expect(handler.vm.jobStatus).toBe(null);
    const jobparams = handler.findComponent(JobParams);
    jobparams.vm.$emit("job-created", "new-job-id");

    await flushPromises();

    expect(router.push).toHaveBeenCalledWith({
      name: "Job View",
      params: { jobId: "new-job-id" }
    });
  });
  it("test data-uploaded handling", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    // @ts-expect-error
    jest.spyOn(handler.vm, "handleData");

    // @ts-expect-error
    expect(handler.vm.handleData).not.toHaveBeenCalled();

    await flushPromises();

    const uploader = handler.findComponent(CSVUpload);
    uploader.vm.$emit("data-uploaded");

    await flushPromises();
    // @ts-expect-error
    expect(handler.vm.handleData).toHaveBeenCalled();
  });
  it("test result status messages", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const expected = {
      running: "Running",
      complete: "Ready",
      queued: "Queued",
      incomplete: "Calculation Not Submitted"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();
    for (const status in expected) {
      handler.vm.$data.job.status.status = status;
      // @ts-expect-error
      expect(handler.vm.resultsStatus).toBe(expected[status]);
    }
  });
  it("test submitstatus messages", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const expected = {
      prepared: "Ready For Calculation",
      complete: "Submitted",
      queued: "Submitted",
      incomplete: "Data Upload Required"
    };

    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();
    for (const status in expected) {
      handler.vm.$data.job.status.status = status;
      // @ts-expect-error
      expect(handler.vm.submitStatus).toBe(expected[status]);
    }
  });
  it("test job steps from job", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();

    expect(handler.vm.$data.job).toStrictEqual(testJob);
    // @ts-expect-error
    expect(handler.vm.jobSteps).toStrictEqual([
      "setup",
      "original weather data",
      "submit",
      "results"
    ]);
  });
  it("test job steps at setup", async () => {
    const propsData = {
      systemId: fetchBody.object_id,
      typeOfJob: "calculate"
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();
    // @ts-expect-error
    expect(handler.vm.jobSteps).toStrictEqual(["setup"]);

    // @ts-expect-error
    expect(handler.vm.dataObjectStatus()).toBe("Calculation Setup Required");
  });
  it("test data step status", async () => {
    const data_objects = [
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/inverters/0/arrays/0",
          type: "original weather data",
          present: false
        }
      },
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd83",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/inverters/0/arrays/0",
          type: "actual weather data",
          present: false
        }
      }
    ];
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();

    handler.vm.$data.job.data_objects = data_objects;

    // @ts-expect-error
    expect(handler.vm.dataStepStatus).toStrictEqual({
      "original weather data": "Needs data",
      "actual weather data": "Needs data"
    });

    data_objects[0].definition.present = true;
    // @ts-expect-error
    expect(handler.vm.dataStepStatus).toStrictEqual({
      "original weather data": "Complete",
      "actual weather data": "Needs data"
    });
    // @ts-expect-error
    expect(handler.vm.filteredDataObjects()).toStrictEqual(data_objects);
  });
  it("test job class inference", async () => {
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();
    // @ts-expect-error
    expect(handler.vm.jobClass).toBe("calculate");
    handler.vm.$data.job.definition.parameters.job_type = {
      compare: "predicted and expected performance",
      performance_granularity: "inverter"
    };
    // @ts-expect-error
    expect(handler.vm.jobClass).toBe("compare");
    handler.vm.$data.job.definition.parameters.job_type = {
      calculate: "weather-adjusted performance ratio",
      performance_granularity: "inverter"
    };
  });
  it("test set step", async () => {
    const data_objects = [
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/inverters/0/arrays/0",
          type: "original weather data",
          present: false
        }
      },
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd83",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/inverters/0/arrays/0",
          type: "actual weather data",
          present: false
        }
      }
    ];
    const propsData = {
      jobId: testJob.object_id
    };
    const handler = mount(JobHandler, {
      localVue,
      propsData,
      mocks,
      router
    });
    await flushPromises();

    handler.vm.$data.job.data_objects = data_objects;

    // @ts-expect-error
    handler.vm.setStep();

    expect(handler.vm.$data.step).toBe("original weather data");

    data_objects[0].definition.present = true;

    // @ts-expect-error
    handler.vm.setStep();
    expect(handler.vm.$data.step).toBe("actual weather data");

    handler.vm.$data.job.status.status = "error";

    // @ts-expect-error
    handler.vm.setStep();
    expect(handler.vm.$data.step).toBe("error");

    handler.vm.$data.job.status.status = "prepared";

    // @ts-expect-error
    handler.vm.setStep();
    expect(handler.vm.$data.step).toBe("calculate");

    handler.vm.$data.job.status.status = "complete";

    // @ts-expect-error
    handler.vm.setStep();
    expect(handler.vm.$data.step).toBe("results");
  });
});
