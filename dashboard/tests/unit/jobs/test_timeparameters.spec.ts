import Vue from "vue";
import flushPromises from "flush-promises";
import { createLocalVue, mount, shallowMount, Wrapper } from "@vue/test-utils";

import JobTimeParameters from "@/components/jobs/TimeParameters.vue";

const localVue = createLocalVue();

describe("test timeparameters", () => {
  it("test", async () => {
    const wrapper = mount(JobTimeParameters, {
      localVue
    });
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams")[0]).toEqual([
      {
        start: "2020-01-01T00:00+00:00",
        end: "2020-02-01T00:00+00:00",
        step: 3600,
        timezone: "UTC"
      }
    ]);
    wrapper.find(".end").setValue("2020-01-02T00:00+00:00");

    // @ts-expect-error
    wrapper.vm.emitParams();
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams")[1]).toEqual([
      {
        start: "2020-01-01T00:00+00:00",
        end: "2020-01-02T00:00+00:00",
        step: 3600,
        timezone: "UTC"
      }
    ]);
  });
});
