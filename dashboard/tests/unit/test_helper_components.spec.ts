import Vue from "vue";
import { mount } from "@vue/test-utils";

import flushPromises from "flush-promises";

import HelpPopup from "@/components/Help.vue";

describe("test help popup", () => {
  it("click hide/show", async () => {
    const wrapper = mount(HelpPopup, {
      propsData: { helpText: "Helpful" }
    });
    expect(wrapper.find("div.help-wrapper").classes()).toContain(
      "accessible-hidden"
    );
    const expand = wrapper.find("button");
    expand.trigger("click");
    await Vue.nextTick();
    expect(wrapper.find("div.help-wrapper").exists()).toBe(true);
    expect(wrapper.find("div.help-wrapper").text()).toEqual("Helpful");
    expect(wrapper.find("div.help-wrapper").classes()).not.toContain(
      "accessible-hidden"
    );
    expand.trigger("click");
    await Vue.nextTick();
    expect(wrapper.find("div.help-wrapper").classes()).toContain(
      "accessible-hidden"
    );
  });
});

let fetchMock: any = {};

global.fetch = jest.fn(() => Promise.resolve(fetchMock));

import DBBrowser from "@/components/Browser.vue";

import { SandiaInverterParameters } from "@/types/InverterParameters";

const mockInverters = ["inva", "invb", "invc"];
const mockParams = new SandiaInverterParameters({});
describe("Test Browser Component", () => {
  beforeEach(() => {
    fetchMock = {
      // reset the mocked response so each test can alter as needed.
      ok: true,
      json: jest.fn().mockResolvedValue(mockInverters),
      status: 200
    };
    jest.clearAllMocks();
  });
  it("test load options", async () => {
    const wrapper = mount(DBBrowser, {
      propsData: {
        componentName: "SandiaInverterParameters"
      }
    });
    await flushPromises();
    expect(wrapper.vm.$data.options).toEqual(mockInverters);
    expect(fetch).toHaveBeenCalledWith(
      "/api/parameters/sandiainverterparameters"
    );
    fetchMock.json.mockResolvedValue(mockParams);
    wrapper.find("input").setValue("inva");
    wrapper.find(".search").trigger("click");

    await flushPromises();

    expect(wrapper.vm.$data.selectOptions).toEqual(["inva"]);
    const option = wrapper.findAll("option");
    expect(option).toHaveLength(1);
    expect(wrapper.find("ul").exists()).toBe(false);
    option.at(0).setSelected();

    await flushPromises();

    wrapper.find(".search-reset").trigger("click");

    await flushPromises();

    const allOptions = wrapper.findAll("option");
    expect(allOptions).toHaveLength(3);

    const summary = wrapper.find("ul");
    expect(summary.exists()).toBe(true);
    expect(wrapper.vm.$data.spec).toEqual(mockParams);
    wrapper.find("button.commit").trigger("click");
    await flushPromises();
    // @ts-expect-error
    expect(wrapper.emitted("parameters-selected")[0]).toEqual([
      {
        parameters: mockParams,
        name: "inva"
      }
    ]);
  });
  it("test emit cancel", async () => {
    const wrapper = mount(DBBrowser, {
      propsData: {
        componentName: "SandiaInverterParameters"
      }
    });
    await flushPromises();
    expect(wrapper.vm.$data.options).toEqual(mockInverters);
    expect(fetch).toHaveBeenCalledWith(
      "/api/parameters/sandiainverterparameters"
    );
    wrapper.find("button.cancel").trigger("click");
    await flushPromises();
    expect(wrapper.emitted("cancel-selection")).toBeTruthy();
  });
  it("test adjust values", async () => {
    const wrapper = mount(DBBrowser, {
      propsData: {
        componentName: "SandiaInverterParameters"
      }
    });
    expect(
      // @ts-expect-error
      wrapper.vm.adjustValues({
        v1: 0.0004940000000000001,
        v2: -0.014925999999999998,
        v3: 0.123456789012,
        v4: 12345678901234.123
      })
    ).toEqual({
      v1: 0.000494,
      v2: -0.014926,
      v3: 0.123456789012,
      v4: 12345678901234.123
    });
  });
});
