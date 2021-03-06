<template>
  <div class="model">
    <div v-if="loading">
      Loading...
    </div>
    <div v-if="!loading">
      <div v-if="errorState">
        <!-- TODO: render errors that can't be handled by validation -->
        {{ JSON.stringify(apiErrors, null, 2) }}
      </div>
      <template v-if="system">
        <h1 v-if="systemId == null">New System</h1>

        <button class="download-system" @click="downloadSystem">
          Download System JSON
        </button>
        <button class="save-system" @click="saveSystem" :disabled="!specValid">
          Save System
        </button>
        <file-upload @uploadSuccess="uploadSuccess" />
        <div class="display-summary">
          Display JSON Summary
          <button
            class="data-object-expander"
            v-bind:class="{ opened: displaySummary }"
            @click="displaySummary = !displaySummary"
          ></button>
        </div>
        <div v-if="displaySummary" class="model-summary">
          <pre>{{ JSON.stringify(system, null, 2) }}</pre>
        </div>

        <b class="mt-1">Model:</b>
        <select v-model="model">
          <option v-for="(v, k) in modelPresetOptions" :key="k" :value="k">
            {{ v }}
          </option>
        </select>
        <br />
        <a
          href="#"
          :class="displayAdvanced ? 'open' : ''"
          @click.prevent="displayAdvanced = !displayAdvanced"
        >
          Advanced
        </a>
        <div class="advanced-model-params" v-if="displayAdvanced">
          <b>Transposition Model:</b>
          <input disabled v-model="modelSpec.transposition_model" />
          <br />
          <b>DC Model:</b>
          <input disabled v-model="modelSpec.dc_model" />
          <br />
          <b>AC Model:</b>
          <input disabled v-model="modelSpec.ac_model" />
          <br />
          <b>AOI Model:</b>
          <input disabled v-model="modelSpec.aoi_model" />
          <br />
          <b>Spectral Model:</b>
          <input disabled v-model="modelSpec.spectral_model" />
          <br />
          <b>Temperature Model:</b>
          <input disabled v-model="modelSpec.temperature_model" />
          <br />
        </div>

        <div>
          <system-view
            :exists="systemId != null"
            :parameters="system"
            :model="model"
            @updateValidity="updateSpecValidity"
          />
        </div>
        <button class="save-system" @click="saveSystem" :disabled="!specValid">
          Save System
        </button>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

import { System } from "@/types/System";
import { modelSpecs } from "@/types/ModelSpecification";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";
import { CECModuleParameters } from "@/types/ModuleParameters";

import SystemView from "@/components/model/System.vue";
import FileUpload from "@/components/FileUpload.vue";

import downloadFile from "@/utils/downloadFile";

Vue.component("system-view", SystemView);
Vue.component("file-upload", FileUpload);

@Component
export default class SystemSpec extends Vue {
  @Prop({ default: null }) systemId!: number | null;
  system!: System;
  model!: string;
  loading!: boolean;
  errorState!: boolean;
  apiErrors!: Record<string, any>;
  specValid!: boolean;

  created() {
    if (Object.keys(this.$store.state.systems).length == 0) {
      // If there are no loaded systems, try to load them for system validation
      this.$store.dispatch("fetchSystems");
    }
    if (this.systemId != undefined) {
      this.loadSystem();
    } else {
      this.system = new System({});
      this.loading = false;
    }
  }
  data() {
    return {
      system: this.system,
      modelPresetOptions: {
        pvsyst: "pvsyst-like",
        pvwatts: "pvwatts",
        sam: "SAM"
      },
      model: "sam",
      displaySummary: false,
      displayAdvanced: false,
      loading: false,
      errorState: false,
      apiErrors: {},
      specValid: false
    };
  }
  uploadSuccess(fileMetadata: string) {
    const metadata = JSON.parse(fileMetadata);
    const system = new System(metadata);
    this.system = system;
    this.inferModel();
  }

  /* istanbul ignore next */
  downloadSystem() {
    const contents = new Blob([JSON.stringify(this.system, null, 2)], {
      type: "application/json;charset=utf-8;"
    });
    const filename = `${this.system.name}.json`;
    downloadFile(filename, contents);
  }

  get modelSpec() {
    return modelSpecs[this.model];
  }

  inferModel() {
    if (this.system.inverters.length > 0) {
      const firstInverter = this.system.inverters[0];
      if (
        SandiaInverterParameters.isInstance(firstInverter.inverter_parameters)
      ) {
        if (firstInverter.arrays.length > 0) {
          const firstArray = firstInverter.arrays[0];
          if (CECModuleParameters.isInstance(firstArray.module_parameters)) {
            this.model = "sam";
          } else {
            this.model = "pvsyst";
          }
        }
      } else if (
        PVWattsInverterParameters.isInstance(firstInverter.inverter_parameters)
      ) {
        this.model = "pvwatts";
      }
    }
  }
  async loadSystem() {
    this.loading = true;
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(`/api/systems/${this.systemId}`, {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      })
    });
    if (response.ok) {
      const system = await response.json();
      this.system = new System(system.definition);
      this.inferModel();
      this.loading = false;
    } else {
      this.errorState = true;
      this.apiErrors = {
        error: "System not found."
      };
      this.loading = false;
    }
  }
  async saveSystem() {
    if (this.specValid) {
      const token = await this.$auth.getTokenSilently();
      let apiPath = "/api/systems/";
      if (this.systemId) {
        apiPath = apiPath + this.systemId;
      }
      const response = await fetch(apiPath, {
        method: "post",
        body: JSON.stringify(this.system),
        headers: new Headers({
          Authorization: `Bearer ${token}`
        })
      });
      if (response.ok) {
        this.$router.push("/systems");
      } else {
        this.loading = false;
        this.errorState = true;
        try {
          this.apiErrors = await response.json();
        } catch (error) {
          this.apiErrors = {
            error: `API responded with status code: ${response.status}`
          };
        }
      }
    }
  }
  updateSpecValidity(isValid: boolean) {
    this.specValid = isValid;
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
div.advanced-model-params {
  border: 1px solid black;
  padding: 0.5em;
  width: fit-content;
}
a::after {
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid #0000ee;
  content: "";
  position: absolute;
  margin-top: 7px;
  margin-left: 7px;
}
a.open::after {
  transform: rotate(180deg);
}
.display-summary {
  border-bottom: 1px solid #444;
  padding: 0.25em;
  position: relative;
  display: flex;
}
.model-summary {
  padding: 0 1em;
  background-color: #eee;
  border: 1px solid #ddd;
}
</style>
