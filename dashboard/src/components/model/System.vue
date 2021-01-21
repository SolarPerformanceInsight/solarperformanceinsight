<template>
  <div class="system">
    <div v-if="exists" class="model-field">
      <b>Name:</b>
      <span>{{ parameters.name }}</span>
    </div>
    <model-field
      v-if="!exists"
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="name"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="latitude"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="longitude"
    />
    <button :disabled="!locationValid" @click="lookupElevation">
      Look Up Elevation
    </button>
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="elevation"
    />
    <inverters-view :inverters="parameters.inverters" :model="model" />
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Watch } from "vue-property-decorator";
import { System } from "@/types/System";

import { getElevation } from "@/utils/elevation";

@Component
export default class SystemView extends ModelBase {
  @Prop({ default: false }) exists!: boolean;
  @Prop() parameters!: System;
  @Prop() model!: string;

  get apiComponentName() {
    return "PVSystem";
  }
  @Watch("parameters", { deep: true })
  validate(newSystem: Record<string, any>) {
    const system = newSystem as System;
    this.$validator
      .validate(this.apiComponentName, system)
      .then(this.setValidationResult);
  }
  get locationValid() {
    return !("latitude" in this.errors) && !("longitude" in this.errors);
  }
  setElevation(results: Array<any>, status: any) {
    console.log(results);
    console.log(status);
    if (status == "OK") {
      const elevation: number = results[0].elevation;
      this.parameters["elevation"] = elevation;
    } else {
      console.log("elevation fetch failed");
    }
  }
  lookupElevation() {
    getElevation(
      this.parameters.latitude,
      this.parameters.longitude,
      this.setElevation
    );
  }
}
</script>

<style scoped>
div {
  text-align: left;
}
</style>
