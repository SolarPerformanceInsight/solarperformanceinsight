import Vue from "vue";
import { createLocalVue, mount } from "@vue/test-utils";

import CSVMapper from "@/components/jobs/CSVMapper.vue";
import FieldMapper from "@/components/jobs/FieldMapper.vue";

// test prop constants
const testJob = {
  object_id: "e1772e64-43ac-11eb-92c2-f4939feddd82",
  object_type: "job",
  created_at: "2020-12-11T19:52:00+00:00",
  modified_at: "2020-12-11T19:52:00+00:00",
  definition: {
    system_definition: {
      name: "Test PV System",
      latitude: 33.98,
      longitude: -115.323,
      elevation: 2300,
      inverters: [
        {
          name: "Inverter 1",
          make_model: "ABB__MICRO_0_25_I_OUTD_US_208__208V_",
          inverter_parameters: {
            Pso: 2.08961,
            Paco: 250,
            Pdco: 259.589,
            Vdco: 40,
            C0: -0.000041,
            C1: -0.000091,
            C2: 0.000494,
            C3: -0.013171,
            Pnt: 0.075
          },
          losses: {},
          arrays: [
            {
              name: "Array 1",
              make_model: "Canadian_Solar_Inc__CS5P_220M",
              albedo: 0.2,
              modules_per_string: 7,
              strings: 5,
              tracking: {
                tilt: 20,
                azimuth: 180
              },
              temperature_model_parameters: {
                u_c: 29,
                u_v: 0,
                eta_m: 0.1,
                alpha_absorption: 0.9
              },
              module_parameters: {
                alpha_sc: 0.004539,
                gamma_ref: 1.2,
                mu_gamma: -0.003,
                I_L_ref: 5.11426,
                I_o_ref: 8.10251e-10,
                R_sh_ref: 381.254,
                R_s: 1.06602,
                R_sh_0: 400,
                cells_in_series: 96
              }
            }
          ],
          airmass_model: "kastenyoung1989",
          aoi_model: "physical",
          clearsky_model: "ineichen",
          spectral_model: "no_loss",
          transposition_model: "haydavies"
        }
      ]
    },
    parameters: {
      system_id: "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
      calculate: "reference performance",
      time_parameters: {
        start: "2020-01-01T00:00:00+00:00",
        end: "2020-12-31T23:59:59+00:00",
        step: "15:00",
        timezone: "UTC"
      },
      weather_granularity: "array",
      irradiance_type: "poa",
      temperature_type: "module"
    }
  },
  status: {
    status: "incomplete",
    last_change: "2020-12-11T20:00:00+00:00"
  },
  data_objects: [
    {
      object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
      object_type: "job_data",
      created_at: "2020-12-11T19:52:00+00:00",
      modified_at: "2020-12-11T19:52:00+00:00",
      definition: {
        schema_path: "/inverters/0/arrays/0",
        type: "reference weather data",
        present: false,
        data_columns: [
          "time",
          "poa_global",
          "poa_direct",
          "poa_diffuse",
          "module_temperature"
        ]
      }
    }
  ]
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

// vue test setup
const localVue = createLocalVue();

Vue.component("field-mapper", FieldMapper);

beforeEach(() => jest.clearAllMocks());

describe("Test CSV Mapper", () => {
  it("test csvmapper methods", async () => {
    const propsData = {
      headers: headers,
      granularity: testJob.definition.parameters.weather_granularity,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });

    const inverter = testJob.definition.system_definition.inverters[0];
    const array = inverter.arrays[0];
    const expectedMetadata = {
      parent: inverter,
      ...array
    };
    // @ts-expect-error
    expect(weatherHandler.vm.toMap).toEqual([
      {
        data_object: testJob.data_objects[0],
        metadata: expectedMetadata
      }
    ]);

    // @ts-expect-error
    weatherHandler.vm.checkValidity();
    expect(weatherHandler.vm.$data.isValid).toBe(false);
    // @ts-expect-error
    expect(weatherHandler.vm.refName(0)).toBe("array_0");
    expect(weatherHandler.vm.$data.dataObjectDisplay).toEqual({
      array_0: true
    });
  });
  it("test csvmapper with inverter granularity", async () => {
    const data_objects = [
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/inverters/0",
          type: "reference weather data",
          present: false,
          data_columns: [
            "time",
            "poa_global",
            "poa_direct",
            "poa_diffuse",
            "module_temperature"
          ]
        }
      }
    ];
    const propsData = {
      headers: headers,
      granularity: "inverter",
      system: testJob.definition.system_definition,
      data_objects: data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    expect(weatherHandler.vm.toMap).toEqual([
      {
        data_object: data_objects[0],
        metadata: testJob.definition.system_definition.inverters[0]
      }
    ]);
  });
  it("test csvmapper with system granularity", async () => {
    const data_objects = [
      {
        object_id: "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
        object_type: "job_data",
        created_at: "2020-12-11T19:52:00+00:00",
        modified_at: "2020-12-11T19:52:00+00:00",
        definition: {
          schema_path: "/",
          type: "reference weather data",
          present: false,
          data_columns: [
            "time",
            "poa_global",
            "poa_direct",
            "poa_diffuse",
            "module_temperature"
          ]
        }
      }
    ];
    const propsData = {
      headers: headers,
      granularity: "system",
      system: testJob.definition.system_definition,
      data_objects: data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    expect(weatherHandler.vm.toMap).toEqual([
      {
        data_object: data_objects[0],
        metadata: testJob.definition.system_definition
      }
    ]);
  });
  it("test map time methods", async () => {
    const propsData = {
      headers: headers,
      granularity: testJob.definition.parameters.weather_granularity,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    expect(weatherHandler.vm.indexMapped).toBe(false);
    // @ts-expect-error
    weatherHandler.vm.mapIndex({ target: { value: 0 } });
    // @ts-expect-error
    expect(weatherHandler.vm.indexMapped).toBe(true);
  });
  it("test update mapping", async () => {
    const propsData = {
      headers: headers,
      granularity: testJob.definition.parameters.weather_granularity,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    weatherHandler.vm.updateMapping({
      loc: "/inverters/0/arrays/0",
      ghi: {
        csv_header: {
          header: "global",
          header_index: 1
        }
      }
    });
    expect(weatherHandler.vm.$data.mapping).toEqual({
      "/inverters/0/arrays/0": {
        ghi: {
          csv_header: {
            header: "global",
            header_index: 1
          }
        },
        time: { csv_header: null }
      }
    });
    // @ts-expect-error
    weatherHandler.vm.mapIndex({
      target: {
        value: 0
      }
    });
    expect(weatherHandler.vm.$data.mapping).toEqual({
      "/inverters/0/arrays/0": {
        ghi: { csv_header: { header: "global", header_index: 1 } },
        time: { csv_header: { header: "timestamp", header_index: 0 } }
      }
    });
  });
  it("test use free headers", async () => {
    const propsData = {
      headers: headers,
      granularity: testJob.definition.parameters.weather_granularity,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    weatherHandler.vm.useHeader({ header: "global", header_index: 0 });
    // @ts-expect-error
    weatherHandler.vm.useHeader({ header: "direct", header_index: 1 });
    // @ts-expect-error
    weatherHandler.vm.useHeader({ header: "diffuse", header_index: 2 });
    expect(weatherHandler.vm.$data.usedHeaders).toEqual([0, 1, 2]);
    // @ts-expect-error
    weatherHandler.vm.freeHeader({ header: "direct", header_index: 1 });
    expect(weatherHandler.vm.$data.usedHeaders).toEqual([0, 2]);
  });
  it("test resetmapping", async () => {
    const propsData = {
      headers: headers,
      granularity: testJob.definition.parameters.weather_granularity,
      system: testJob.definition.system_definition,
      data_objects: testJob.data_objects,
      indexField: "time"
    };
    const weatherHandler = mount(CSVMapper, {
      localVue,
      propsData
    });
    // @ts-expect-error
    weatherHandler.vm.updateMapping({
      loc: "/inverters/0/arrays/0",
      ghi: { csv_header: "global" }
    });
    expect(weatherHandler.vm.$data.mapping).toEqual({
      "/inverters/0/arrays/0": {
        ghi: { csv_header: "global" },
        time: { csv_header: null }
      }
    });
    // @ts-expect-error
    weatherHandler.vm.resetMapping();
    expect(weatherHandler.vm.$data.mapping).toEqual({});
    expect(weatherHandler.vm.$data.usedHeaders).toEqual([]);
    expect(weatherHandler.vm.$data.indexHeader).toEqual(null);
  });
});
