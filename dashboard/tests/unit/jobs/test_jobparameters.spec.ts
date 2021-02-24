import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import JobParams from "@/components/jobs/parameters/JobParams.vue";
import CalculateJobParams from "@/components/jobs/parameters/CalculateJobParams.vue";
import CompareJobParams from "@/components/jobs/parameters/CompareJobParams.vue";
import CalculatePRJobParams from "@/components/jobs/parameters/CalculatePRJobParams.vue";
import TimeParameters from "@/components/jobs/parameters/TimeParameters.vue";

import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

import * as Jobs from "@/api/jobs";
import { $auth } from "../mockauth";
import { DateTime } from "luxon";

const now = DateTime.fromISO("2020-01-01T00:00+00:00");

// @ts-expect-error
const dt = jest.spyOn(DateTime, "now");
dt.mockImplementation(() => now);

Vue.component("calculate-job-params", CalculateJobParams);
Vue.component("compare-job-params", CompareJobParams);
Vue.component("calculatepr-job-params", CalculatePRJobParams);
Vue.component("time-parameters", TimeParameters);

// test prop constants
const testSystem = new StoredSystem({
  object_id: "uuid",
  object_type: "system",
  created_at: "2021-01-01T00:00+00:00",
  modified_at: "2021-01-01T00:00+00:00",
  definition: new System({
    inverters: [
      new Inverter({
        arrays: [new PVArray({})]
      })
    ]
  })
});

const defaultTimeParams = {
  start: "2020-01-01T00:00:00.000Z",
  end: "2020-01-01T00:00:00.000Z",
  step: 3600,
  timezone: "America/Denver"
};
// vue test setup
const localVue = createLocalVue();

const mockJobCreate = jest.spyOn(Jobs, "create");

const mockJobResponse = {
  ok: true,
  json: jest.fn().mockResolvedValue({ object_id: "jobid" }),
  status: 201
};

// @ts-expect-error
mockJobCreate.mockResolvedValue(mockJobResponse);

const mocks = {
  $auth
};

beforeEach(() => {
  // reset the response to a success so that special failure cases can change
  // to whatever they want.
  mockJobResponse.ok = true;
  mockJobResponse.json = jest.fn().mockResolvedValue({ object_id: "jobid" });
  mockJobResponse.status = 201;
});
describe("Test Job Parameters", () => {
  it("test expected inputs exist", async () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData,
      mocks
    });
    // @ts-expect-error
    expect(wrapper.vm.jobParamComponent).toBe("calculate-job-params");

    // irradiance type
    expect(wrapper.find("input#standard").exists()).toBe(true);
    expect(wrapper.find("input#poa").exists()).toBe(true);
    expect(wrapper.find("input#effective").exists()).toBe(true);

    // temperature
    expect(wrapper.find("input#cell").exists()).toBe(true);
    expect(wrapper.find("input#module").exists()).toBe(true);
    expect(wrapper.find("input#air").exists()).toBe(true);

    // granularity
    expect(wrapper.find("input#system").exists()).toBe(true);
    expect(wrapper.find("input#inverter").exists()).toBe(true);
    expect(wrapper.find("input#array").exists()).toBe(true);

    const effective = wrapper.find("input#effective");
    // @ts-expect-error
    effective.element.selected = true;
    effective.trigger("change");

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.jobSpec).toEqual({
      system_id: testSystem.object_id,
      calculate: "predicted performance",
      time_parameters: defaultTimeParams,
      weather_granularity: "system",
      irradiance_type: "effective",
      temperature_type: "air"
    });
    expect(wrapper.findComponent(TimeParameters).exists()).toBe(true);
    wrapper.find("button").trigger("click");
    await flushPromises();

    expect(mockJobCreate).toHaveBeenCalled();
    // @ts-expect-error
    expect(wrapper.emitted("job-created")[0]).toEqual(["jobid"]);
  });
  it("test post failure with api errors", async () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData,
      mocks
    });
    mockJobResponse.ok = false;
    mockJobResponse.status = 422;
    (mockJobResponse.json = jest.fn().mockResolvedValue({ detail: "broken" })),
      wrapper.find("button").trigger("click");
    await flushPromises();

    expect(wrapper.find("div.errors").text()).toBe("broken");
  });
  it("test post failure without api errors", async () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData,
      mocks
    });
    mockJobResponse.ok = false;
    wrapper.find("button").trigger("click");
    await flushPromises();

    expect(wrapper.find("div.errors").text()).toBe(
      '{\n  "error": "Failed to start job with error code 201"\n}'
    );
  });

  it("test loading calculate params", () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData
    });
    expect(wrapper.findComponent(CalculateJobParams).exists()).toBe(true);
  });
  it("test loading compare params", () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "compare"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData
    });
    expect(wrapper.findComponent(CompareJobParams).exists()).toBe(true);
  });
  it("test loading calculate pr params", () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculatepr"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData
    });
    expect(wrapper.findComponent(CalculatePRJobParams).exists()).toBe(true);
  });
});
describe("Test Calculate Parameters", () => {
  it("test expected inputs exist", async () => {
    const wrapper = mount(CalculateJobParams, {
      localVue
    });
    expect(wrapper.find("input#predicted-performance").exists()).toBe(true);
    expect(wrapper.find("input#expected-performance").exists()).toBe(true);
  });
  it("test emits on change", async () => {
    const wrapper = mount(CalculateJobParams, {
      localVue
    });
    expect(wrapper.find("input#predicted-performance").exists()).toBe(true);
    expect(wrapper.find("input#expected-performance").exists()).toBe(true);

    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params")[0]).toEqual([
      {
        calculate: "predicted performance"
      }
    ]);

    const expected = wrapper.find("input#expected-performance");
    // @ts-expect-error
    expected.element.selected = true;
    expected.trigger("change");

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params")[1]).toEqual([
      {
        calculate: "expected performance"
      }
    ]);
  });
});
