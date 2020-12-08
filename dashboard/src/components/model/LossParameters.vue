<template>
  <div class="loss-parameters">
    <div v-if="model == 'pvwatts'">
      <model-field
        field-name="soiling"
        input-type="number" />
      <model-field
        field-name="shading"
        input-type="number" />
      <model-field
        field-name="snow"
        input-type="number" />
      <model-field
        field-name="mismatch"
        input-type="number" />
      <model-field
        field-name="wiring"
        input-type="number" />
      <model-field
        field-name="connections"
        input-type="number" />
      <model-field
        field-name="lid"
        input-type="number" />
      <model-field
        field-name="nameplate_rating"
        input-type="number" />
      <model-field
        field-name="age"
        input-type="number" />
      <model-field
        field-name="availability"
        input-type="number" />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";

// Update with many classes of inverter parameters to check for type before
// choosing a display.
import { PVWattsLosses } from "@/types/Losses";

@Component
export default class LossParametersView extends ModelBase {
  @Prop() parameters!: PVWattsLosses | null;

  @Prop() model!: string;
  errors: Record<string, any> = {};

  get apiComponentName() {
    return "PVWattsLosses";
  }
  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    if (this.model == "pvwatts") {
      this.$validator
        .validate(this.apiComponentName, newParams as PVWattsLosses)
        .then(this.setValidationResult);
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
div.loss-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
