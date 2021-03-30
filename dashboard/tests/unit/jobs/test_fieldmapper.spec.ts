import flushPromises from "flush-promises";
import { createLocalVue, mount } from "@vue/test-utils";

import FieldMapper from "@/components/jobs/FieldMapper.vue";

import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import { SingleAxisTrackingParameters } from "@/types/Tracking";

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

const comp = {
  data_object: {
    object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
    object_type: "job_data",
    created_at: "2020-12-11T19:52:00+00:00",
    modified_at: "2020-12-11T19:52:00+00:00",
    definition: {
      schema_path: "/",
      type: "reference weather data",
      present: false,
      data_columns: ["time", "ghi", "dni", "dhi"]
    }
  },
  metadata: testSystem.definition
};

const monthlyComp = {
  data_object: {
    object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
    object_type: "job_data",
    created_at: "2020-12-11T19:52:00+00:00",
    modified_at: "2020-12-11T19:52:00+00:00",
    definition: {
      schema_path: "/",
      type: "reference monthly weather data",
      present: false,
      data_columns: [
        "month",
        "total_poa_insolation",
        "average_daytime_cell_temperature"
      ]
    }
  },
  metadata: testSystem.definition
};

const headers = [
  {
    header: "timestamp",
    header_index: 0
  },
  {
    header: "global",
    header_index: 1
  },
  {
    header: "direct",
    header_index: 2
  },
  {
    header: "diffuse",
    header_index: 3
  }
];

const usedHeaders: Array<string> = [];

const required = comp.data_object.definition.data_columns;

// vue test setup
const localVue = createLocalVue();

describe("Test field mapper", () => {
  it("test system", () => {
    const propsData = {
      headers,
      usedHeaders,
      comp,
      show: true,
      indexField: "time"
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    const fields = wrapper.findAll("li");
    expect(fields).toHaveLength(required.length - 1);
    fields.wrappers.forEach(f => {
      const headerOptions = f.findAll("option");
      expect(headerOptions).toHaveLength(headers.length + 1);
      expect(headerOptions.wrappers[0].text()).toBe("Not included");
      headerOptions.wrappers.slice(1).forEach(o => {
        expect(headers.map((x: any) => x.header).includes(o.text())).toBe(true);
      });
    });
  });
  it("test monthly", () => {
    const propsData = {
      headers,
      usedHeaders,
      comp: monthlyComp,
      show: true,
      indexField: "month"
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    const fields = wrapper.findAll("li");
    expect(fields).toHaveLength(2);
    fields.wrappers.forEach(f => {
      const headerOptions = f.findAll("option");
      expect(headerOptions).toHaveLength(headers.length + 1);
      expect(headerOptions.wrappers[0].text()).toBe("Not included");
      headerOptions.wrappers.slice(1).forEach(o => {
        expect(headers.map((x: any) => x.header).includes(o.text())).toBe(true);
      });
    });
  });
  it("test Fixed PVArray", () => {
    const theArray = testSystem.definition.inverters[0].arrays[0];
    const theInverter = testSystem.definition.inverters[0];
    // @ts-expect-error
    theArray["parent"] = theInverter;
    const arrayComp = { ...comp };
    // @ts-expect-error
    arrayComp.metadata = theArray;
    const propsData = {
      headers,
      usedHeaders,
      comp: arrayComp,
      show: true,
      indexField: "time"
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    const metaLabels = wrapper.findAll("b");
    expect(metaLabels.wrappers[0].text()).toBe("Module Make and Model:");
    expect(metaLabels.wrappers[1].text()).toBe("Surface Tilt:");
    expect(metaLabels.wrappers[2].text()).toBe("Surface Azimuth:");
    expect(metaLabels.wrappers[3].text()).toBe("Inverter Name:");
    expect(metaLabels.wrappers[4].text()).toBe("Inverter Make and Model:");
    const fields = wrapper.findAll("li");
    expect(fields).toHaveLength(required.length - 1);
    fields.wrappers.forEach(f => {
      const headerOptions = f.findAll("option");
      expect(headerOptions).toHaveLength(headers.length + 1);
      expect(headerOptions.wrappers[0].text()).toBe("Not included");
      headerOptions.wrappers.slice(1).forEach(o => {
        expect(headers.map((x: any) => x.header).includes(o.text())).toBe(true);
      });
    });
  });
  it("test Fixed PVArray", () => {
    const theArray = new PVArray({
      tracking: new SingleAxisTrackingParameters({})
    });
    const theInverter = testSystem.definition.inverters[0];
    // @ts-expect-error
    theArray["parent"] = theInverter;
    const arrayComp = { ...comp };
    // @ts-expect-error
    arrayComp.metadata = theArray;
    const propsData = {
      headers,
      usedHeaders,
      comp: arrayComp,
      show: true,
      indexField: "time"
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    const metaLabels = wrapper.findAll("b");
    expect(metaLabels.wrappers[0].text()).toBe("Module Make and Model:");
    expect(metaLabels.wrappers[1].text()).toBe("Axis Tilt:");
    expect(metaLabels.wrappers[2].text()).toBe("Axis Azimuth:");
    expect(metaLabels.wrappers[3].text()).toBe("Inverter Name:");
    expect(metaLabels.wrappers[4].text()).toBe("Inverter Make and Model:");
    const fields = wrapper.findAll("li");
    expect(fields).toHaveLength(required.length - 1);
    fields.wrappers.forEach(f => {
      const headerOptions = f.findAll("option");
      expect(headerOptions).toHaveLength(headers.length + 1);
      expect(headerOptions.wrappers[0].text()).toBe("Not included");
      headerOptions.wrappers.slice(1).forEach(o => {
        expect(headers.map((x: any) => x.header).includes(o.text())).toBe(true);
      });
    });
  });
  it("test Inverter", () => {
    const theInverter = testSystem.definition.inverters[0];
    const inverterComp = { ...comp };
    // @ts-expect-error
    inverterComp.metadata = theInverter;
    const propsData = {
      headers,
      usedHeaders,
      comp: inverterComp,
      show: true,
      indexField: "time"
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    const metaLabels = wrapper.findAll("b");
    expect(metaLabels.wrappers[0].text()).toBe("Make and Model:");
    const fields = wrapper.findAll("li");
    expect(fields).toHaveLength(required.length - 1);
    fields.wrappers.forEach(f => {
      const headerOptions = f.findAll("option");
      expect(headerOptions).toHaveLength(headers.length + 1);
      expect(headerOptions.wrappers[0].text()).toBe("Not included");
      headerOptions.wrappers.slice(1).forEach(o => {
        expect(headers.map((x: any) => x.header).includes(o.text())).toBe(true);
      });
    });
  });
  it("test methods", async () => {
    const propsData = {
      headers,
      usedHeaders,
      comp,
      show: true
    };
    const wrapper = mount(FieldMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    expect(wrapper.vm.metadata).toEqual(comp.metadata);

    // @ts-expect-error
    wrapper.vm.addMapping({
      variable: "ghi",
      csv_header: "someheader"
    });
    await flushPromises();

    expect(wrapper.vm.$data.mapping["ghi"]).toEqual({
      csv_header: "someheader"
    });
    // @ts-expect-error
    expect(wrapper.emitted("mapping-updated")[0]).toBeTruthy();
    // @ts-expect-error
    expect(wrapper.emitted("used-header")[0]).toEqual(["someheader"]);

    // @ts-expect-error
    wrapper.vm.addMapping({
      variable: "ghi",
      csv_header: "otherheader"
    });
    await flushPromises();

    expect(wrapper.vm.$data.mapping["ghi"]).toEqual({
      csv_header: "otherheader"
    });
    // @ts-expect-error
    expect(wrapper.emitted("mapping-updated")[1]).toBeTruthy();
    // @ts-expect-error
    expect(wrapper.emitted("free-header")[0]).toEqual(["someheader"]);
    // @ts-expect-error
    expect(wrapper.emitted("used-header")[1]).toEqual(["otherheader"]);

    // @ts-expect-error
    wrapper.vm.addMapping({ csv_header: "Not included", variable: "ghi" });
    await flushPromises();

    expect("ghi" in wrapper.vm.$data.mapping).toBe(false);
    // @ts-expect-error
    expect(wrapper.emitted("mapping-updated")[2]).toBeTruthy();
    // @ts-expect-error
    expect(wrapper.emitted("free-header")[1]).toEqual(["otherheader"]);

    // @ts-expect-error
    expect(wrapper.vm.isValid()).toBe(false);
    required.forEach(r => {
      // @ts-expect-error
      wrapper.vm.addMapping({ csv_header: r, variable: r });
    });
    await flushPromises();

    // @ts-expect-error
    expect(wrapper.vm.isValid()).toBe(true);

    // @ts-expect-error
    expect(wrapper.vm.getDisplayName("time")).toBe("Timestamp");
  });
});
