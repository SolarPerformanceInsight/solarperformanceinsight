import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import JobParams from "@/components/jobs/parameters/JobParams.vue";
import CalculateJobParams from "@/components/jobs/parameters/CalculateJobParams.vue";
import CompareJobParams from "@/components/jobs/parameters/CompareJobParams.vue";
import CalculatePRJobParams from "@/components/jobs/parameters/CalculatePRJobParams.vue";
import TimeParameters from "@/components/jobs/parameters/TimeParameters.vue";
import DatetimeField from "@/components/jobs/parameters/DatetimeField.vue";
import DataParamHandler from "@/components/jobs/parameters/DataParamHandler.vue";
import DataParams from "@/components/jobs/parameters/DataParams.vue";

import APIErrors from "@/components/ErrorRenderer.vue";
import HelpPopup from "@/components/Help.vue";

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
Vue.component("help", HelpPopup);

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
    const div = document.createElement("div");
    div.id = "root";
    document.body.appendChild(div);

    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      attachTo: "#root",
      localVue,
      propsData,
      mocks
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.jobParamComponent).toBe("calculate-job-params");

    // irradiance type
    expect(wrapper.find("input[value='standard']").exists()).toBe(true);
    expect(wrapper.find("input[value='poa']").exists()).toBe(true);
    expect(wrapper.find("input[value='effective']").exists()).toBe(true);

    // temperature
    expect(wrapper.find("input[value='cell']").exists()).toBe(true);
    expect(wrapper.find("input[value='module']").exists()).toBe(true);
    expect(wrapper.find("input[value='air']").exists()).toBe(true);

    // granularity
    expect(wrapper.find("input[value='system']").exists()).toBe(true);
    expect(wrapper.find("input[value='inverter']").exists()).toBe(true);
    expect(wrapper.find("input[value='array']").exists()).toBe(true);

    const effective = wrapper.find("input[value='effective']");
    // @ts-expect-error
    effective.element.selected = true;
    effective.trigger("change");

    const startend = wrapper.findAllComponents(DatetimeField);
    const start = startend.wrappers[0];
    start.vm.$data.year = 2020;
    start.vm.$data.month = 1;
    start.vm.$data.day = 1;
    start.vm.$data.hour = 0;
    start.vm.$data.minute = 0;

    // @ts-expect-error
    start.vm.emitTimeParams();
    await flushPromises();

    const end = startend.wrappers[1];

    end.vm.$data.year = 2020;
    end.vm.$data.month = 2;
    end.vm.$data.day = 1;
    end.vm.$data.hour = 0;
    end.vm.$data.minute = 0;

    // @ts-expect-error
    end.vm.emitTimeParams();
    await flushPromises();

    const timeparams = wrapper.findComponent(TimeParameters);

    // @ts-expect-error
    timeparams.vm.emitParams();

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.jobSpec).toEqual({
      system_id: testSystem.object_id,
      calculate: "predicted performance",
      time_parameters: {
        start: "2020-01-01T00:00:00.000-07:00",
        end: "2020-02-01T00:00:00.000-07:00",
        step: 3600,
        timezone: "America/Denver"
      },
      weather_granularity: "system",
      irradiance_type: "effective",
      temperature_type: "air"
    });
    // @ts-expect-error
    expect(wrapper.vm.isValid).toBe(true);
    expect(wrapper.findComponent(TimeParameters).exists()).toBe(true);

    const button = wrapper.find("button[type=submit]");
    button.trigger("click");
    await flushPromises();

    expect(mockJobCreate).toHaveBeenCalled();
    // @ts-expect-error
    expect(wrapper.emitted("job-created")[0]).toEqual(["jobid"]);
    wrapper.destroy();
  });
  it("test post failure with api errors", async () => {
    const div = document.createElement("div");
    div.id = "root";
    document.body.appendChild(div);
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      attachTo: "#root",
      localVue,
      propsData,
      mocks
    });

    const startend = wrapper.findAllComponents(DatetimeField);
    const start = startend.wrappers[0];
    start.vm.$data.year = 2020;
    start.vm.$data.month = 1;
    start.vm.$data.day = 1;
    start.vm.$data.hour = 0;
    start.vm.$data.minute = 0;

    // @ts-expect-error
    start.vm.emitTimeParams();
    await flushPromises();

    const end = startend.wrappers[1];

    end.vm.$data.year = 2020;
    end.vm.$data.month = 2;
    end.vm.$data.day = 1;
    end.vm.$data.hour = 0;
    end.vm.$data.minute = 0;

    // @ts-expect-error
    end.vm.emitTimeParams();
    await flushPromises();

    const timeparams = wrapper.findComponent(TimeParameters);
    // @ts-expect-error
    timeparams.vm.emitParams();

    await flushPromises();

    mockJobResponse.ok = false;
    mockJobResponse.status = 422;
    mockJobResponse.json = jest.fn().mockResolvedValue({
      detail: [
        {
          loc: ["place"],
          msg: "broken",
          type: "error"
        }
      ]
    });
    wrapper.find("button[type=submit]").trigger("click");
    await flushPromises();

    expect(wrapper.findComponent(APIErrors).exists()).toBe(true);
    wrapper.destroy();
  });
  it("test post failure without api errors", async () => {
    const div = document.createElement("div");
    div.id = "root";
    document.body.appendChild(div);
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      attachTo: "#root",
      localVue,
      propsData,
      mocks
    });

    const startend = wrapper.findAllComponents(DatetimeField);
    const start = startend.wrappers[0];
    start.vm.$data.year = 2020;
    start.vm.$data.month = 1;
    start.vm.$data.day = 1;
    start.vm.$data.hour = 0;
    start.vm.$data.minute = 0;

    // @ts-expect-error
    start.vm.emitTimeParams();
    await flushPromises();

    const end = startend.wrappers[1];

    end.vm.$data.year = 2020;
    end.vm.$data.month = 2;
    end.vm.$data.day = 1;
    end.vm.$data.hour = 0;
    end.vm.$data.minute = 0;

    // @ts-expect-error
    end.vm.emitTimeParams();
    await flushPromises();

    const timeparams = wrapper.findComponent(TimeParameters);
    // @ts-expect-error
    timeparams.vm.emitParams();

    await flushPromises();

    mockJobResponse.ok = false;
    wrapper.find("button[type=submit]").trigger("click");
    await flushPromises();

    expect(wrapper.findComponent(APIErrors).text()).toBe("");
    wrapper.destroy();
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
  it("test monthly comparejob", async () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "compare"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData,
      mocks
    });
    const compareParams = {
      compare: "monthly predicted and actual performance"
    };

    wrapper.vm.$data.jobTypeParams = compareParams;
    // @ts-expect-error
    expect(wrapper.vm.isMonthly).toBe(true);
    // @ts-expect-error
    expect(wrapper.vm.isValid).toBe(true);
    // @ts-expect-error
    expect(wrapper.vm.jobSpec).toEqual({
      system_id: testSystem.object_id,
      ...compareParams
    });
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
describe("Test Compare Parameters", () => {
  it("test emit correct fields", async () => {
    const wrapper = mount(CompareJobParams, {
      localVue
    });

    await flushPromises();

    wrapper.vm.$data.timeResolution = "monthly";
    wrapper.vm.$data.compare = "predicted and actual performance";

    await flushPromises();

    wrapper.vm.$data.compare = "expected and actual performance";

    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params").length).toBe(3);

    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params")[0]).toEqual([
      {
        compare: "predicted and actual performance"
      }
    ]);

    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params")[1]).toEqual([
      {
        compare: "monthly predicted and actual performance"
      }
    ]);

    // @ts-expect-error
    expect(wrapper.emitted("new-job-type-params")[0]).toEqual([
      {
        compare: "predicted and actual performance"
      }
    ]);
  });
  it("test ensure timeres", async () => {
    const wrapper = mount(CompareJobParams, {
      localVue
    });

    wrapper.find("input[value='monthly']").trigger("click");

    await flushPromises();

    expect(wrapper.vm.$data.timeResolution).toBe("monthly");

    // trigger no effect
    wrapper.find("input[value='monthly']").trigger("click");

    await flushPromises();

    expect(wrapper.vm.$data.timeResolution).toBe("monthly");

    wrapper
      .find("input[value='expected and actual performance']")
      .trigger("click");

    await flushPromises();

    expect(wrapper.vm.$data.timeResolution).toBe("leHourly");
  });
});
describe("Test DataParamHandler", () => {
  it("test requiredDataParams", async () => {
    const propsData = {
      jobTypeParams: {
        calculate: "predicted performance"
      }
    };
    const wrapper = mount(DataParamHandler, {
      localVue,
      propsData
    });
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["predicted"]);

    wrapper.setProps({
      jobTypeParams: {
        calculate: "expected"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["expected"]);

    wrapper.setProps({
      jobTypeParams: {
        calculate: "weather-adjusted performance ratio"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["expected and actual"]);

    wrapper.setProps({
      jobTypeParams: {
        compare: "expected and actual performance"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["expected and actual"]);

    wrapper.setProps({
      jobTypeParams: {
        compare: "predicted and actual performance"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["predicted", "actual"]);

    wrapper.setProps({
      jobTypeParams: {
        compare: "predicted and expected performance"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual(["predicted", "expected"]);
    wrapper.setProps({
      jobTypeParams: {
        compare: "monthly predicted and actual performance"
      }
    });
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.requiredDataParams).toEqual([]);
  });
});
describe("Test DataParams", () => {
  // default parameters
  const base_parameters = {
    irradiance_type: "standard",
    weather_granularity: "system",
    temperature_type: "air"
  };
  it("test parameters for predicted", async () => {
    const propsData = {
      dataType: "predicted",
      jobClass: "compare"
    };

    const wrapper = mount(DataParams, {
      propsData
    });

    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "predicted_data_parameters",
      parameters: {
        data_available: "weather only",
        ...base_parameters
      }
    });

    wrapper.vm.$data.data_available = "weather and AC performance";
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "predicted_data_parameters",
      parameters: {
        data_available: "weather and AC performance",
        performance_granularity: "system",
        ...base_parameters
      }
    });
  });
  it("test parameters for other", async () => {
    const propsData = {
      dataType: "expected",
      jobClass: "compare"
    };

    const wrapper = mount(DataParams, {
      propsData
    });

    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "expected_data_parameters",
      parameters: {
        performance_granularity: "system",
        ...base_parameters
      }
    });

    wrapper.setProps({
      dataType: "actual",
      jobClass: "compare"
    });

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "actual_data_parameters",
      parameters: {
        performance_granularity: "system",
        ...base_parameters
      }
    });

    wrapper.setProps({
      dataType: "expected",
      jobClass: "calculate"
    });

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "data_parameters",
      parameters: {
        performance_granularity: "system",
        ...base_parameters
      }
    });

    wrapper.setProps({
      dataType: "expected and actual",
      jobClass: "compare"
    });

    await flushPromises();
    // @ts-expect-error
    expect(wrapper.vm.parameters).toEqual({
      type: "data_parameters",
      parameters: {
        performance_granularity: "system",
        ...base_parameters
      }
    });
  });
});
