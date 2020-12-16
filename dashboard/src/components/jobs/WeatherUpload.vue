<template>
  <div class="weather-upload">
  <slot>Upload your weather data</slot>
  <br />
  <label for="weather-upload">Select a weather file:</label>
  <input
    id="weather-upload"
    type="file"
    accept="text/csv"
    @change="processFile"/>
    <template v-if="promptForMapping">
      <weather-csv-mapper
        :system="system"
        :weather_granularity="weather_granularity"
        :weather_type="weather_type"
        :headers="headers" />
    </template>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import FileUpload from "@/components/FileUpload.vue";
import { StoredSystem } from "@/types/System";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

@Component
export default class WeatherUpload extends Vue {
  @Prop() weather_granularity!: string;
  @Prop() weather_type!: string;
  @Prop() system!: StoredSystem;
  mapping!: Record<string, string>;
  promptForMapping!: boolean;
  headers!: Array<string>;
  data() {
    return {
      mapping: {},
      promptForMapping: false,
      headers: []
    }
  }
  mapAndStoreCSV(csv: string) {
    console.log(csv);
    if (csv.indexOf("\n")){
      this.headers = csv.slice(0, csv.indexOf("\n")).split(",");
      this.promptForMapping = true;;
    } else {
      console.log("Bad csv");
    }
      }
  processMapping(newMapping: Record<string, string>) {
    this.mapping = newMapping;
  }
  processFile(e: HTMLInputEvent) {
    if (e.target.files !== null) {
      const fileList = e.target.files;
      const file = e.target.files[0];
      const reader = new FileReader();
      // @ts-expect-error
      reader.onload = f => this.mapAndStoreCSV(f.target.result);
      reader.readAsText(file);
    }
  }
}
</script>
<style scoped>
div.weather-upload {
  border: 1px solid black;
  padding: 1em;
}
</div>
