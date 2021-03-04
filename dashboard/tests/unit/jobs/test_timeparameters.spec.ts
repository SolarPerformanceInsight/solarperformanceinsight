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
        start: null,
        end: null,
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams").length).toBe(1);

    wrapper.find("input.year").setValue(2020);
    wrapper.find("input.month").setValue(2020);
    wrapper.find("input.day").setValue(2020);
    wrapper.find("input.hour").setValue(2020);
    wrapper.find("input.minute").setValue(2020);
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
