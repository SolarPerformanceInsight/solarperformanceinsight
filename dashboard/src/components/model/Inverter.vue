<template>
  <li>
    <b>System Name:</b>
    {{ $parent.$parent.parameters.name }}
    <br />
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
    <button @click="removeInverter">Remove Inverter</button>
    <br />
    <button @click="duplicateInverter">Duplicate Inverter</button>
  </li>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";
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
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.parameters.inverter_parameters = new SandiaInverterParameters({});
      this.parameters.losses = null;
    } else if (newModel == "pvwatts") {
      this.parameters.inverter_parameters = new PVWattsInverterParameters({});
      this.parameters.losses = new PVWattsLosses({});
    }
  }

  removeInverter() {
    // @ts-expect-error
    this.$parent.inverters.splice(this.index, 1);
  }
  duplicateInverter() {
    // @ts-expect-error
    this.$parent.inverters.push(new Inverter(this.parameters));
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