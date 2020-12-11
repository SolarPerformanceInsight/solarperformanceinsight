import Vue from "vue";
import { createLocalVue, mount } from "@vue/test-utils";

import HelpPopup from "@/components/Help.vue";

describe("test help popup", () => {
  it("click hide/show", async () => {
    const wrapper = mount(HelpPopup, {
      propsData: { helpText: "Helpful" }
    });
    expect(wrapper.find("div.help-wrapper").exists()).toBe(false);
    const expand = wrapper.find("button");
    expand.trigger("click");
    await Vue.nextTick();
    expect(wrapper.find("div.help-wrapper").exists()).toBe(true);
    expect(wrapper.find("div.help-wrapper").text()).toEqual("Helpful");
    expand.trigger("click");
    await Vue.nextTick();
    expect(wrapper.find("div.help-wrapper").exists()).toBe(false);
  });
});
