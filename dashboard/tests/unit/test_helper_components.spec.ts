import Vue from "vue";
import { mount } from "@vue/test-utils";

import flushPromises from "flush-promises";

import HelpPopup from "@/components/Help.vue";

import APIErrors from "@/components/ErrorRenderer.vue";

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
    expect(wrapper.emitted("parameters-selected")[0]).toStrictEqual([
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
});
describe("Test Error Renderer", () => {
  const errors = [
    {
      loc: ["this", "is", "location"],
      msg: "Borked",
      type: "Value Error"
    },
    {
      loc: ["this", "thing", "__root__"],
      msg: "Borked badder",
      type: "Value Error"
    }
  ]
  it("test all errors", async () => {
    const wrapper = mount(APIErrors, {
      propsData: {
        errors
      }
    });
    await flushPromises();
    const errorList = wrapper.findAll("li");
    expect(errorList.length).toBe(2);
    expect(errorList.wrappers[0].text()).toBe(
      "location:\n      Borked"
    );
    expect(errorList.wrappers[1].text()).toBe(
      "thing:\n      Borked badder"
    );
  });
  it("test filtered errors", async () => {
    const wrapper = mount(APIErrors, {
      propsData: {
        errors,
        fields: ["thing"]
      }
    });
    await flushPromises();
    const errorList = wrapper.findAll("li");
    expect(errorList.length).toBe(1);
    expect(errorList.wrappers[0].text()).toBe(
      "thing:\n      Borked badder"
    );
  });


});
