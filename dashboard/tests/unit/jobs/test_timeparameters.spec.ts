import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import JobTimeParameters from "@/components/jobs/parameters/TimeParameters.vue";

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
        start: "",
        end: "",
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams").length).toBe(1);

    wrapper.find(".vdatetime").trigger("click");
    await flushPromises();
    wrapper.vm.$data.start = "2020-01-01T00:00:00Z";
    wrapper.vm.$data.end = "2020-02-01T00:00:00";
    wrapper.find(".vdatetime").trigger("click");
    // @ts-expect-error
    wrapper.vm.emitParams();
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams")[1]).toEqual([
      {
        start: "2020-01-01T00:00:00Z",
        end: "2020-02-01T00:00:00",
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
  });
});
