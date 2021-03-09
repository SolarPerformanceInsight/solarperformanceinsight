<template>
  <li>
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
      field-name="make_model"
    />
    <b>Inverter Parameters:</b>
    <br />
    <inverter-parameters
      @parameters-selected="loadInverterParameters"
      :parameters="parameters.inverter_parameters"
      :model="model"
    />
    <span v-if="model == 'pvwatts'">
      <b>Loss Parameters:</b>
      <br />
      <loss-parameters :parameters="parameters.losses" :model="model" />
    </span>
    <arrays-view :pvarrays="parameters.arrays" :model="model" />
    <br />
    <button class="remove-inverter" @click="removeInverter">
      Remove Inverter
    </button>
    <br />
    <button class="duplicate-inverter" @click="duplicateInverter">
      Duplicate Inverter
    </button>
  </li>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Watch } from "vue-property-decorator";
import { Inverter } from "@/types/Inverter";
import { PVWattsLosses } from "@/types/Losses";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

@Component
export default class InverterView extends ModelBase {
  @Prop() parameters!: Inverter;
  @Prop() index!: number;
  @Prop() model!: string;

  @Watch("model")
  changeModel(newModel: string, oldModel: string) {
    if (newModel == "pvsyst" || newModel == "sam") {
      let current_params = {};
      if (oldModel == "pvsyst" || oldModel == "sam") {
        current_params = this.parameters.inverter_parameters;
      }
      this.parameters.inverter_parameters = new SandiaInverterParameters(
        current_params
      );
      if ("losses" in this.parameters) {
        delete this.parameters.losses;
      }
    } else if (newModel == "pvwatts") {
      this.parameters.inverter_parameters = new PVWattsInverterParameters({});
      this.parameters.losses = new PVWattsLosses({});
    }
  }

  removeInverter() {
    this.$emit("inverter-removed", this.index);
  }
  duplicateInverter() {
    this.$emit("inverter-added", this.parameters);
  }
  get apiComponentName() {
    return "Inverter";
  }

  @Watch("parameters", { deep: true })
  validate(newInverter: Record<string, any>) {
    const inverter = newInverter as Inverter;
    this.$validator
      .validate(this.apiComponentName, inverter)
      .then(this.setValidationResult);
  }

  loadInverterParameters({
    parameters,
    name
  }: {
    parameters: Record<string, any>;
    name: string;
  }) {
    this.parameters.make_model = name;
    // only supported for pvsyst model
    this.parameters.inverter_parameters = new SandiaInverterParameters(
      parameters
    );
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li.inverter {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
