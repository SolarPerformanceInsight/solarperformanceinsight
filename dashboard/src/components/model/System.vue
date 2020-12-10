<template>
  <div class="system">
    <model-field
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

import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { System } from "@/types/System";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

@Component
export default class SystemView extends ModelBase {
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
}
</script>

<style scoped>
div {
  text-align: left;
}
</style>
