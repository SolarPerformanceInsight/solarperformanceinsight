<template>
  <div class="model">
    <button @click="displaySummary = !displaySummary">Display Summary</button>
    <button @click="downloadMetadata">Download Metadata</button>
    <div v-if="displaySummary" class="model-summary">
      <h1>Model Summary</h1>
      <pre>{{ JSON.stringify(system, null, 2) }}</pre>
    </div>
    <file-upload @uploadSuccess="uploadSuccess" />
    <div>
      <system-view :system="system" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { System } from "@/types/System";
import SystemView from "@/components/System.vue";
import FileUpload from "@/components/FileUpload.vue";

Vue.component("system-view", SystemView);
Vue.component("file-upload", FileUpload);

@Component
export default class Model extends Vue {
  system!: System;
  data() {
    return {
      system: this.system ? this.system : new System(),
      displaySummary: false
    };
  }
  components = ["system-view", "file-upload"];
  uploadSuccess(fileMetadata: string) {
    const metadata = JSON.parse(fileMetadata);
    const system = new System(metadata);
    this.system = system;
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
</style>
