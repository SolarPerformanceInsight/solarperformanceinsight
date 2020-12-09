<template>
  <div class="model">
    <div v-if="loading">
      Loading...
    </div>
    <div v-if="errorState">
      An error occured.
    </div>
    <div v-if="!loading && !errorState">
      <h1 v-if="systemId == null">New System</h1>
      <button @click="displaySummary = !displaySummary">
        Display JSON Summary
      </button>
      <button @click="downloadSystem">Download System JSON</button>
      <button @click="saveSystem">Save System</button>
      <div v-if="displaySummary" class="model-summary">
        <h1>Model Summary</h1>
        <pre>{{ JSON.stringify(system, null, 2) }}</pre>
      </div>
      <file-upload @uploadSuccess="uploadSuccess" />

      <b>Model:</b>
      <select v-model="model">
        <option v-for="m in modelPresetOptions" :key="m">{{ m }}</option>
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
        <system-view :parameters="system" :model="model" />
      </div>
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

import SystemView from "@/components/model/System.vue";
import FileUpload from "@/components/FileUpload.vue";

Vue.component("system-view", SystemView);
Vue.component("file-upload", FileUpload);

@Component
export default class SystemSpec extends Vue {
  @Prop({ default: null }) systemId!: number | null;
  system!: System;
  model!: string;
  loading!: boolean;
  errorState!: boolean;

  created() {
    if (this.systemId != undefined) {
      // Ensure that a new system is created from the System found in
      // the store, so as not to inadvertently mangle stored systems.
      this.system = new System(this.$store.state.systems[this.systemId]);
    } else {
      this.system = new System({});
      this.loading = false;
    }
  }
  data() {
    return {
      system: this.system ? this.system : new System({}),
      modelPresetOptions: ["pvsyst", "pvwatts"],
      model: "pvsyst",
      displaySummary: false,
      displayAdvanced: false,
      loading: false,
      errorState: false
    };
  }
  components = ["system-view", "file-upload"];
  uploadSuccess(fileMetadata: string) {
    const metadata = JSON.parse(fileMetadata);
    const system = new System(metadata);
    this.system = system;
    this.inferModel();
  }

  downloadSystem() {
    const contents = new Blob([JSON.stringify(this.system, null, 2)], {
      type: "application/json;charset=utf-8;"
    });
    const filename = `${this.system.name}.json`;
    if (navigator.msSaveBlob) {
      navigator.msSaveBlob(contents, filename);
    } else {
      const link = document.createElement("a");
      link.href = URL.createObjectURL(contents);
      link.download = filename;
      link.target = "_blank";
      link.style.visibility = "hidden";
      link.dispatchEvent(new MouseEvent("click"));
      link.remove();
    }
  }

  get modelSpec() {
    return modelSpecs[this.model];
  }

  inferModel() {
    if (this.system.inverters.length > 0) {
      const firstParams = this.system.inverters[0].inverter_parameters;

      if (SandiaInverterParameters.isInstance(firstParams)) {
        this.model = "pvsyst";
      } else if (PVWattsInverterParameters.isInstance(firstParams)) {
        this.model = "pvwatts";
      }
    }
  }

  async saveSystem() {
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(`/api/systems/`, {
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
    }
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
</style>