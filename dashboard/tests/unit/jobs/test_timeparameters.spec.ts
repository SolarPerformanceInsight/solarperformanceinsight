import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import JobTimeParameters from "@/components/jobs/parameters/TimeParameters.vue";
import { DateTime } from "luxon";

const localVue = createLocalVue();
const now = DateTime.fromISO("2020-01-01T00:00+00:00");

// @ts-expect-error
const dt = jest.spyOn(DateTime, "now");
dt.mockImplementation(() => now);

describe("test timeparameters", () => {
  it("test", async () => {
    const wrapper = mount(JobTimeParameters, {
      localVue
    });
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams")[0]).toEqual([
      {
        start: "2020-01-01T00:00:00.000Z",
        end: "2020-01-01T00:00:00.000Z",
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams").length).toBe(1);

    wrapper.find(".vdatetime").trigger("click");
    await flushPromises();

    wrapper.find(".vdatetime").trigger("click");
    // @ts-expect-error
    wrapper.vm.emitParams();
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.emitted("new-timeparams")[1]).toEqual([
      {
        start: "2020-01-01T00:00:00.000Z",
        end: "2020-01-01T00:00:00.000Z",
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
  });
});
