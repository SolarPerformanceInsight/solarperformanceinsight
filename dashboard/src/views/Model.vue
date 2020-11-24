<template>
  <div class="model">
    <h1 v-if="systemId == null">New System</h1>
    <button @click="displaySummary = !displaySummary">Display Summary</button>
    <button @click="downloadMetadata">Download System</button>
    <button @click="saveMetadata">Save System</button>
    <div v-if="displaySummary" class="model-summary">
      <h1>Model Summary</h1>
      <pre>{{ JSON.stringify(system, null, 2) }}</pre>
    </div>
    <file-upload @uploadSuccess="uploadSuccess" />

    <b>Model: </b>
    <select v-model="model">
      <option v-for="m in modelPresetOptions" :key="m">{{ m }}</option> </select
    ><br />
    <a
      href="#"
      :class="displayAdvanced ? 'open' : ''"
      @click.prevent="displayAdvanced = !displayAdvanced"
    >
      Advanced
    </a>
    <div class="advanced-model-params" v-if="displayAdvanced">
      <b>Transposition Model: </b>
      <input disabled v-model="modelSpec.transposition_model" /><br />
      <b>DC Model: </b>
      <input disabled v-model="modelSpec.dc_model" /><br />
      <b>AC Model: </b>
      <input disabled v-model="modelSpec.ac_model" /><br />
      <b>AOI Model: </b>
      <input disabled v-model="modelSpec.aoi_model" /><br />
      <b>Spectral Model: </b>
      <input disabled v-model="modelSpec.spectral_model" /><br />
      <b>Temperature Model: </b>
      <input disabled v-model="modelSpec.temperature_model" /><br />
    </div>

    <div>
      <system-view :system="system" :model="model" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

import { System } from "@/types/System";
import { modelSpecs } from "@/types/ModelSpecification";
import {
  PVSystInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

import SystemView from "@/components/System.vue";
import FileUpload from "@/components/FileUpload.vue";

Vue.component("system-view", SystemView);
Vue.component("file-upload", FileUpload);

@Component
export default class Model extends Vue {
  @Prop({default: null}) systemId!: number | null;
  system!: System;
  model!: string;

  created() {
    if (this.systemId != undefined) {
      this.system = new System(this.$store.state.systems[this.systemId]);
    }
  }
  data() {
    return {
      system: this.system ? this.system : new System({}),
      modelPresetOptions: ["pvsyst", "pvwatts"],
      model: "pvsyst",
      displaySummary: false,
      displayAdvanced: false
    };
  }
  components = ["system-view", "file-upload"];
  uploadSuccess(fileMetadata: string) {
    const metadata = JSON.parse(fileMetadata);
    const system = new System(metadata);
    this.system = system;
    this.inferModel();
  }
  downloadMetadata() {
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
  saveMetadata() {
    // TODO: make post request with auth
    console.log(this.system);
  }
  get modelSpec() {
    return modelSpecs[this.model];
  }
  inferModel() {
    if (this.system.inverters.length > 0) {
      const firstParams = this.system.inverters[0].inverter_parameters;

      if (PVSystInverterParameters.isInstance(firstParams)) {
        this.model = "pvsyst";
      } else if (PVWattsInverterParameters.isInstance(firstParams)) {
        this.model = "pvwatts";
      }
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
