import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import JobTimeParameters from "@/components/jobs/parameters/TimeParameters.vue";
import DatetimeField from "@/components/jobs/parameters/DatetimeField.vue";

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

    // @ts-expect-error
    wrapper.vm.emitParams();
    await flushPromises();

    const emitted = wrapper.emitted("new-timeparams");
    // @ts-expect-error
    expect(emitted[emitted.length - 1]).toEqual([
      {
        start: "2020-01-01T00:00:00.000-07:00",
        end: "2020-02-01T00:00:00.000-07:00",
        step: 3600,
        timezone: "America/Denver"
      }
    ]);
  });
});
