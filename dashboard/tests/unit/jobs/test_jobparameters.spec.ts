import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import JobParams from "@/components/jobs/parameters/JobParams.vue";
import CalculateJobParams from "@/components/jobs/parameters/CalculateJobParams.vue";
import CompareJobParams from "@/components/jobs/parameters/CompareJobParams.vue";
import CalculatePRJobParams from "@/components/jobs/parameters/CalculatePRJobParams.vue";
import TimeParameters from "@/components/jobs/parameters/TimeParameters.vue"

import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import { SingleAxisTrackingParameters } from "@/types/Tracking";

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
  start: "2020-01-01T00:00+00:00",
  end: "2020-02-01T00:00+00:00",
  step: 3600,
  timezone: "UTC"
}
// vue test setup
const localVue = createLocalVue();

describe("Test Job Parameters", () => {
  it("test expected inputs exist", async () => {
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData
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
      job_type: {
        calculate: "predicted performance"
      },
      time_parameters: defaultTimeParams,
      weather_granularity: "system",
      irradiance_type: "effective",
      temperature_type: "cell"
    })
    expect(wrapper.findComponent(TimeParameters).exists()).toBe(true);
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
    const propsData = {
      systemId: testSystem.object_id,
      system: testSystem.definition,
      jobClass: "calculate"
    };
    const wrapper = mount(JobParams, {
      localVue,
      propsData
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
      job_type: {
        calculate: "predicted performance"
      },
      time_parameters: defaultTimeParams,
      weather_granularity: "system",
      irradiance_type: "effective",
      temperature_type: "cell"
    })
    expect(wrapper.findComponent(TimeParameters).exists()).toBe(true);
  });
});
